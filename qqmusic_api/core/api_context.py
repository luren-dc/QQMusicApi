"""API Context 管理类. 维护全局请求环境、会话与参数构造逻辑."""

import time
from collections.abc import Sequence
from typing import Any, cast

import anyio
import orjson as json
from niquests import AsyncSession
from niquests.exceptions import RequestException

from ..algorithms import zzc_sign
from ..models.request import Credential
from ..utils.device import Device, DeviceManager
from ..utils.qimei import QimeiManager
from .exceptions import HTTPError, NetworkError
from .versioning import DEFAULT_VERSION_POLICY, Platform, VersionPolicy


class ApiContext:
    """全局请求上下文与会话管理."""

    def __init__(
        self,
        credential: Credential | None = None,
        *,
        platform: Platform | None = None,
        device_path: str | None = None,
        version_policy: VersionPolicy = DEFAULT_VERSION_POLICY,
        session: AsyncSession,
    ) -> None:
        """初始化 ApiContext.

        Args:
            credential: 全局默认凭证.
            platform: 全局默认请求平台.
            device_path: 设备信息文件路径.
            version_policy: 版本策略规则.
            session: HTTP 异步 Session.
        """
        self.credential = credential or Credential()
        self.platform = platform or Platform.ANDROID
        self.version_policy = version_policy
        self._session = session
        self._device_store = DeviceManager(device_path)
        self._session_lock = anyio.Lock()
        self._qimei_manager = QimeiManager(
            device_store=self._device_store,
            app_version=self.version_policy.get_qimei_app_version(),
            sdk_version=self.version_policy.get_qimei_sdk_version(),
            session=self._session,
        )

    async def get_user_agent(self, platform: Platform | None = None) -> str:
        """根据指定或默认平台生成请求所需的 User-Agent.

        Args:
            platform: 平台标识. 若为 None, 使用当前上下文默认平台.

        Returns:
            格式化好的 User-Agent 字符串.
        """
        target_platform = platform or self.platform
        return self.version_policy.get_user_agent(target_platform, await self._device_store.get_device())

    async def ensure_session(self, platform: Platform | None = None) -> None:
        """校验并更新平台会话信息 (针对 Android 平台)."""
        target_platform = platform or self.platform
        if target_platform != Platform.ANDROID:
            return

        def _is_session_valid(dev: Device) -> bool:
            return (
                dev.session_save_time is not None
                and (int(time.time()) - dev.session_save_time) < 86400
                and bool(dev.session_uid and dev.session_sid)
            )

        device = await self._device_store.get_device()
        if _is_session_valid(device):
            return

        async with self._session_lock:
            device = await self._device_store.get_device()
            if _is_session_valid(device):
                return

            finalcomm = self.version_policy.build_comm(
                platform=Platform.ANDROID,
                credential=self.credential,
                device=device,
                qimei=cast("dict[str, str]", await self._qimei_manager.get_cached()),
                guid=device.open_udid,
            )
            payload: dict[str, Any] = {
                "comm": finalcomm,
                "req_0": {
                    "module": "music.getSession.session",
                    "method": "GetSession",
                    "param": {
                        "uid": device.session_uid or "",
                        "vkey": 0,
                        "caller": 0,
                    },
                },
            }
            user_agent = await self.get_user_agent(Platform.ANDROID)
            try:
                resp = await self._session.post(
                    "https://u.y.qq.com/cgi-bin/musicu.fcg",
                    json=payload,
                    headers={"User-Agent": user_agent},
                )
                await self._session.gather(resp)
            except RequestException as exc:
                raise NetworkError(str(exc)) from exc

            if resp.status_code != 200:
                raise HTTPError(
                    f"HTTP 请求状态码异常: {resp.status_code}",
                    status_code=cast("int", resp.status_code),
                )

            resp_data = resp.json()
            session_data = resp_data["req_0"]["data"]["session"]
            device.session_uid = str(session_data["uid"])
            device.session_sid = session_data["sid"]
            device.session_vkey = session_data.get("vkey")
            device.session_save_time = int(time.time())
            await self._device_store.save_device()

    async def prepare_http_kwargs(
        self,
        credential: Credential | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """准备标准 HTTP 请求所需要的 kwargs (注入 Cookies 和 User-Agent).

        Args:
            credential: 请求凭证, 优先于上下文默认凭证.
            platform: 请求平台, 优先于上下文默认平台.
            **kwargs: 额外请求参数.

        Returns:
            组装好的 kwargs 字典.
        """
        prepared = kwargs.copy()
        cred = credential or self.credential
        user_cookies = prepared.pop("cookies", {})
        cookies: dict[str, str] = {}
        if cred.musicid:
            cookies["uin"] = cred.str_musicid or str(cred.musicid)
            cookies["qqmusic_uin"] = cred.str_musicid or str(cred.musicid)
        if cred.musickey:
            cookies["qm_keyst"] = cred.musickey
            cookies["qqmusic_key"] = cred.musickey
        cookies.update(user_cookies)
        if cookies:
            prepared["cookies"] = cookies

        headers = prepared.get("headers", {})
        if "User-Agent" not in headers:
            headers["User-Agent"] = await self.get_user_agent(Platform.WEB)
        prepared["headers"] = headers

        return prepared

    async def build_api_kwargs(
        self,
        data: Sequence[dict[str, Any]],
        comm: dict[str, Any] | None = None,
        credential: Credential | None = None,
        platform: Platform | None = None,
        *,
        override_comm: bool = False,
        sign: bool = False,
    ) -> tuple[str, dict[str, Any], dict[str, str], dict[str, str]]:
        """构建 CGI 接口调用的 URL、payload、params 与 headers.

        Args:
            data: 请求子项列表.
            comm: 自定义公共参数.
            credential: 请求凭证.
            platform: 请求平台.
            override_comm: 是否完全覆盖默认公共参数.
            sign: 是否需要签名 URL.

        Returns:
            (url, payload, params, headers) 四元组.
        """
        target_platform = platform or self.platform
        if target_platform == Platform.ANDROID:
            await self.ensure_session(target_platform)

        device = await self._device_store.get_device()
        if override_comm:
            final = (comm or {}).copy()
        else:
            final = self.version_policy.build_comm(
                platform=target_platform,
                credential=credential or self.credential,
                device=device,
                qimei=cast("dict[str, str]", await self._qimei_manager.get_cached())
                if target_platform == Platform.ANDROID
                else None,
                guid=device.open_udid,
            )
            if comm:
                final.update(comm)

        user_agent = await self.get_user_agent(target_platform)

        payload: dict[str, Any] = {
            "comm": final,
        }
        params: dict[str, str] = {}
        for idx, req in enumerate(data):
            payload[f"req_{idx}"] = req

        if sign:
            params["_"] = str(int(time.time() * 1000))
            params["sign"] = zzc_sign(json.dumps(payload))

        url = "https://u.y.qq.com/cgi-bin/musicu.fcg" if not sign else "https://u.y.qq.com/cgi-bin/musics.fcg"
        headers = {"User-Agent": user_agent}

        return url, payload, params, headers
