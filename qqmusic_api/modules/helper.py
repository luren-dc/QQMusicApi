"""辅助功能 API. 提供各类零散的辅助接口."""

from typing import Literal

from ..models.helper import (
    FinishUploadResponse,
    FinishUploadResultDict,
    InitUploadFileDict,
    InitUploadResponse,
)
from ..models.request import Credential
from ._base import ApiModule

# songlist, songcover, homepage, cmtaudio, moment, moment_video, moment_video_cover, musiclog, Aiplassistant
BUSINESS_TYPE = Literal["songlist", "homepage", "Aiplassistant"]


class HelperApi(ApiModule):
    """辅助功能 API."""

    def init_upload(
        self,
        bus_id: BUSINESS_TYPE,
        files: list[InitUploadFileDict],
        *,
        credential: Credential | None = None,
    ):
        """初始化 COS 上传以获取临时凭证.

        Tips:
            具备 `cos-python-sdk-v5` 高级接口所需的所有权限.

        Args:
            bus_id: 业务 ID, 例如 "songlist", "avatar" 等.
            files: 待上传文件信息列表, 每项需包含 "FileSha1", "FileName", "FileSize".
            credential: 请求凭证.
        """
        return self._build_cgi(
            module="music.filesys.FileSystem",
            method="InitUpload",
            param={
                "BusID": bus_id,
                "Files": files,
            },
            preserve_bool=False,
            sign=True,
            require_login=True,
            credential=credential,
            response_model=InitUploadResponse,
        )

    def finish_upload(
        self,
        bus_id: BUSINESS_TYPE,
        results: list[FinishUploadResultDict],
        *,
        credential: Credential | None = None,
    ):
        """完成 COS 上传并通知服务器验证.

        Args:
            bus_id: 业务 ID.
            results: 上传结果列表, 每项需包含 Storage 字典等信息.
            credential: 请求凭证.
        """
        return self._build_cgi(
            module="music.filesys.FileSystem",
            method="FinishUpload",
            param={
                "BusID": bus_id,
                "Results": results,
            },
            preserve_bool=False,
            sign=True,
            require_login=True,
            credential=credential,
            response_model=FinishUploadResponse,
        )
