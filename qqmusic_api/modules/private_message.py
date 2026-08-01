"""私信相关 API 模块."""

from typing import Any

from ..core import Platform
from ..core.pagination import MultiFieldContinuationStrategy
from ..models.private_message import (
    PrivateChatEntriesResponse,
    PrivateConfigResponse,
    PrivateMediaMessageDetailsResponse,
    PrivateMessageListResponse,
    PrivateMusicianCardResponse,
    PrivateOperationResponse,
    PrivateSafetyHintResponse,
    PrivateSendMessageResponse,
    PrivateSessionListResponse,
)
from ..models.request import Credential
from ._base import ApiModule

PRIVATE_MSG_READ_MODULE = "music.privateMsg.PrivateMsgRead"
PRIVATE_MSG_WRITE_MODULE = "music.privateMsg.PrivateMsgWrite"


def _build_session_list_next_params(
    params: dict[str, Any], response: PrivateSessionListResponse
) -> dict[str, Any] | None:
    """根据最后一个会话构造会话列表下一页参数."""
    if not response.sessions:
        return None
    last_session = response.sessions[-1]
    return {**params, "last_id": last_session.session_id, "last_time": last_session.sort_time}


def _build_message_list_next_params(
    params: dict[str, Any], response: PrivateMessageListResponse
) -> dict[str, Any] | None:
    """根据最后一条消息构造消息列表下一页参数."""
    if not response.messages:
        return None
    return {**params, "last_id": response.messages[-1].id}


class PrivateMessageApi(ApiModule):
    """私信相关 API 模块类.

    所有接口固定使用 Android 平台.
    """

    def get_sessions(
        self,
        last_id: str = "",
        *,
        order: int = 1,
        size: int = 20,
        last_time: int = 0,
        from_: int = 0,
        fans_flag: int | None = 1,
        encrypt_from_uin: str | None = None,
        credential: Credential | None = None,
    ):
        """获取私信会话列表.

        Args:
            last_id: 上一页最后一个会话 ID.
            order: 排序方向.
            size: 返回数量.
            last_time: 上一页最后一个会话排序时间.
            from_: 会话来源.
            fans_flag: 粉丝或超级私信标记; 传入 encrypt_from_uin 时不会下发.
            encrypt_from_uin: 超级私信艺人加密 UIN; 优先级高于 fans_flag.
            credential: 请求凭证.
        """
        params: dict[str, Any] = {
            "last_id": last_id,
            "order": order,
            "size": size,
            "last_time": last_time,
            "from": from_,
        }
        if encrypt_from_uin:
            params["EncryptFromUin"] = encrypt_from_uin
        elif fans_flag is not None:
            params["FansFlag"] = fans_flag

        return self._build_request(
            PRIVATE_MSG_READ_MODULE,
            "GetSessionList",
            params,
            credential=credential,
            require_login=True,
            platform=Platform.ANDROID,
            response_model=PrivateSessionListResponse,
            pager_strategy=MultiFieldContinuationStrategy[PrivateSessionListResponse](
                _build_session_list_next_params,
                has_more_extractor=lambda r: r.has_more == 1,
                context_name="private_message_session_list",
            ),
        ).with_extractor(lambda r: r.sessions)

    def delete_session(self, session_id: str, *, super_msg_flag: int = 0, credential: Credential | None = None):
        """删除私信会话.

        Args:
            session_id: 会话 ID.
            super_msg_flag: 超级私信标记.
            credential: 请求凭证.
        """
        return self._build_request(
            PRIVATE_MSG_WRITE_MODULE,
            "DeleteSession",
            {"session_id": session_id, "super_msg_flag": super_msg_flag},
            credential=credential,
            require_login=True,
            platform=Platform.ANDROID,
            response_model=PrivateOperationResponse,
        )

    def get_messages(
        self,
        *,
        session_id: str = "",
        user_id: str = "",
        last_id: str = "",
        wns_id: str = "",
        order: int = 1,
        size: int = 50,
        flag: int = 0,
        location_id: str | None = None,
        update_time: int | None = None,
        credential: Credential | None = None,
    ):
        """获取私信聊天消息列表.

        Args:
            session_id: 会话 ID.
            user_id: 对端用户 UIN.
            last_id: 上一页最后一条消息 ID.
            wns_id: WNS 消息 ID.
            order: 排序方向.
            size: 返回数量.
            flag: 消息加载标记.
            location_id: 本地记录的定位消息 ID.
            update_time: 客户端发送消息更新时间.
            credential: 请求凭证.
        """
        params: dict[str, Any] = {"order": order, "size": size, "flag": flag}
        optional_params = {
            "session_id": session_id,
            "last_id": last_id,
            "wns_id": wns_id,
            "user_id": user_id,
            "location_id": location_id,
            "update_time": update_time,
        }
        params.update({key: value for key, value in optional_params.items() if value not in (None, "")})

        return self._build_request(
            PRIVATE_MSG_READ_MODULE,
            "GetMessage",
            params,
            credential=credential,
            require_login=True,
            platform=Platform.ANDROID,
            response_model=PrivateMessageListResponse,
            pager_strategy=MultiFieldContinuationStrategy[PrivateMessageListResponse](
                _build_message_list_next_params,
                has_more_extractor=lambda r: r.has_more == 1,
                context_name="private_message_list",
            ),
        ).with_extractor(lambda r: r.messages)

    def send_message(
        self,
        user_id: str,
        msg_type: int,
        *,
        session_id: str = "",
        last_id: str = "",
        last_msg_seq: int = 0,
        meta_data: dict[str, Any] | None = None,
        entrance: int = 0,
        client_key: str = "",
        source_flag: int | None = None,
        msg_id: str | None = None,
        user_input: str | None = None,
        super_msg_flag: int | None = 0,
        star_send: bool = False,
        credential: Credential | None = None,
    ):
        """发送私信消息.

        Args:
            user_id: 对端用户 UIN.
            msg_type: 消息类型.
            session_id: 会话 ID.
            last_id: 最后一条消息 ID.
            last_msg_seq: 最后一条消息序列号.
            meta_data: 消息元数据.
            entrance: 发送入口.
            client_key: 客户端消息键.
            source_flag: 来源标记.
            msg_id: 重发时的原消息 ID.
            user_input: 用户输入原文.
            super_msg_flag: 超级私信标记.
            star_send: 是否使用明星超级私信发送接口.
            credential: 请求凭证.
        """
        params: dict[str, Any] = {
            "last_msg_seq": last_msg_seq,
            "user_id": user_id,
            "entrance": entrance,
            "client_key": client_key,
            "msg_type": msg_type,
        }
        optional_params = {
            "session_id": session_id,
            "last_id": last_id,
            "meta_data": meta_data,
            "source_flag": source_flag,
            "msg_id": msg_id,
            "user_input": user_input,
            "super_msg_flag": super_msg_flag,
        }
        params.update({key: value for key, value in optional_params.items() if value not in (None, "")})

        return self._build_request(
            PRIVATE_MSG_WRITE_MODULE,
            "StarSendSuperMsg" if star_send else "SendMessageAsync",
            params,
            credential=credential,
            require_login=True,
            platform=Platform.ANDROID,
            response_model=PrivateSendMessageResponse,
        )

    def delete_message(
        self,
        session_id: str,
        msg_id: str,
        *,
        super_msg_flag: int = 0,
        credential: Credential | None = None,
    ):
        """删除单条私信消息.

        Args:
            session_id: 会话 ID.
            msg_id: 消息 ID.
            super_msg_flag: 超级私信标记.
            credential: 请求凭证.
        """
        return self._build_request(
            PRIVATE_MSG_WRITE_MODULE,
            "DeleteMessage",
            {"session_id": session_id, "msg_id": msg_id, "super_msg_flag": super_msg_flag},
            credential=credential,
            require_login=True,
            platform=Platform.ANDROID,
            response_model=PrivateOperationResponse,
        )

    def clear_session(
        self,
        session_id: str,
        *,
        super_msg_flag: int = 0,
        credential: Credential | None = None,
    ):
        """清空私信会话消息.

        Args:
            session_id: 会话 ID.
            super_msg_flag: 超级私信标记.
            credential: 请求凭证.
        """
        return self._build_request(
            PRIVATE_MSG_WRITE_MODULE,
            "ClearSession",
            {"session_id": session_id, "super_msg_flag": super_msg_flag},
            credential=credential,
            require_login=True,
            platform=Platform.ANDROID,
            response_model=PrivateOperationResponse,
        )

    def set_config(
        self,
        config_type: int,
        config_value: str,
        *,
        credential: Credential | None = None,
    ):
        """写入私信配置.

        Args:
            config_type: 配置类型.
            config_value: 配置值字符串.
            credential: 请求凭证.
        """
        return self._build_request(
            PRIVATE_MSG_WRITE_MODULE,
            "SetConfig",
            {"config_type": config_type, "config_value_str": config_value},
            credential=credential,
            require_login=True,
            platform=Platform.ANDROID,
            response_model=PrivateOperationResponse,
        )

    def get_config(
        self,
        config_type: int,
        config_value: str = "",
        *,
        credential: Credential | None = None,
    ):
        """读取私信配置.

        Args:
            config_type: 配置类型.
            config_value: 配置值字符串.
            credential: 请求凭证.
        """
        return self._build_request(
            PRIVATE_MSG_READ_MODULE,
            "GetConfig",
            {"config_type": config_type, "config_value_str": config_value},
            credential=credential,
            require_login=True,
            platform=Platform.ANDROID,
            response_model=PrivateConfigResponse,
        )

    def get_musician_message_card(
        self,
        enc_uin: str,
        *,
        credential: Credential | None = None,
    ):
        """获取音乐人私信卡片.

        Args:
            enc_uin: 加密 UIN.
            credential: 请求凭证.
        """
        return self._build_request(
            "music.privateMsg.MusicianMsgCardSvr",
            "GetMusicianCard",
            {"EncUin": enc_uin},
            credential=credential,
            require_login=True,
            platform=Platform.ANDROID,
            response_model=PrivateMusicianCardResponse,
        )

    def report_card_message_action(
        self,
        target_user_id: str,
        msg_type: int,
        confirm: int,
        msg_id: str,
        *,
        credential: Credential | None = None,
        ext: dict[str, Any] | None = None,
    ):
        """上报卡片消息操作回调.

        Args:
            target_user_id: 目标用户 ID.
            msg_type: 消息类型.
            confirm: 确认值.
            msg_id: 消息 ID.
            credential: 请求凭证.
            ext: 扩展字段.
        """
        params: dict[str, Any] = {
            "target_user_id": target_user_id,
            "msg_type": msg_type,
            "confirm": confirm,
            "msg_id": msg_id,
        }
        if ext:
            params["ext"] = ext
        return self._build_request(
            PRIVATE_MSG_WRITE_MODULE,
            "ActCardMsgCallBack",
            params,
            credential=credential,
            require_login=True,
            platform=Platform.ANDROID,
            response_model=PrivateOperationResponse,
        )

    def get_chat_entries(
        self,
        scenes: list[int],
        *,
        from_user_type: int | None = None,
        user_id: str | None = None,
        ext: dict[str, str] | None = None,
        credential: Credential | None = None,
    ):
        """获取聊天页功能入口.

        Args:
            scenes: 入口场景列表.
            from_user_type: 来源用户类型.
            user_id: 对端用户 UIN.
            ext: 扩展字段.
            credential: 请求凭证.
        """
        params = {
            "Scence": scenes,
            "FromUserType": from_user_type,
            "UserID": user_id,
            "Ext": ext,
        }
        return self._build_request(
            PRIVATE_MSG_READ_MODULE,
            "GetEntries",
            {key: value for key, value in params.items() if value is not None},
            credential=credential,
            require_login=True,
            platform=Platform.ANDROID,
            response_model=PrivateChatEntriesResponse,
        )

    def get_media_message_details(
        self,
        session_id: str,
        msg_ids: list[str],
        *,
        credential: Credential | None = None,
    ):
        """获取图片或视频消息详情.

        Args:
            session_id: 会话 ID.
            msg_ids: 消息 ID 列表.
            credential: 请求凭证.
        """
        return self._build_request(
            PRIVATE_MSG_READ_MODULE,
            "GetMsgDetails",
            {"SessionID": session_id, "MsgIDs": msg_ids},
            credential=credential,
            require_login=True,
            platform=Platform.ANDROID,
            response_model=PrivateMediaMessageDetailsResponse,
        )

    def mark_all_messages_read(
        self,
        cmd_flag: int,
        encrypt_uin: str,
        *,
        credential: Credential | None = None,
    ):
        """设置私信全部已读.

        Args:
            cmd_flag: 命令标记.
            encrypt_uin: 加密 UIN.
            credential: 请求凭证.
        """
        return self._build_request(
            PRIVATE_MSG_WRITE_MODULE,
            "SetAllMsgMardRead",
            {"CmdFlag": cmd_flag, "EncryptUin": encrypt_uin},
            credential=credential,
            require_login=True,
            platform=Platform.ANDROID,
            response_model=PrivateOperationResponse,
        )

    def get_safety_hint(
        self,
        enc_uin: str,
        close: int = 0,
        *,
        credential: Credential | None = None,
    ):
        """获取私信安全提示.

        Args:
            enc_uin: 加密 UIN.
            close: 是否关闭提示.
            credential: 请求凭证.
        """
        return self._build_request(
            PRIVATE_MSG_READ_MODULE,
            "GetSafetyHint",
            {"encUin": enc_uin, "close": close},
            credential=credential,
            require_login=True,
            platform=Platform.ANDROID,
            response_model=PrivateSafetyHintResponse,
        )

    def get_friendship_badge(
        self,
        target_enc_uin: str,
        *,
        credential: Credential | None = None,
    ):
        """获取聊天页好友浮标.

        Args:
            target_enc_uin: 目标用户加密 UIN.
            credential: 请求凭证.
        """
        return self._build_request(
            "music.dazi.DzEntrySrv",
            "GetFriendFloatingIcon",
            {"TargetEncuin": target_enc_uin},
            credential=credential,
            require_login=True,
            platform=Platform.ANDROID,
            response_model=None,
        )
