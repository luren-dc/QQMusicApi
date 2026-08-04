"""私信模块测试."""

import pytest

from qqmusic_api import Client, CredentialInvalidError
from qqmusic_api.models.private_message import PrivateMessageListResponse


async def test_private_message_requires_login(client: Client) -> None:
    """测试私信会话列表需要登录凭证."""
    with pytest.raises(CredentialInvalidError):
        await client.private_message.get_sessions()


def test_message_list_accepts_nullable_pat_map() -> None:
    """测试私信消息列表兼容空拍一拍映射."""
    result = PrivateMessageListResponse.model_validate({"PatMap": None})
    assert result.pat_map == {}


async def test_get_sessions_real_request(authenticated_client: Client) -> None:
    """测试真实获取私信会话列表."""
    result = await authenticated_client.private_message.get_sessions(size=10)
    assert result.sessions is not None
    assert result.has_more in (0, 1)


async def test_get_messages_real_request(authenticated_client: Client) -> None:
    """测试真实获取私信消息列表."""
    session_result = await authenticated_client.private_message.get_sessions(size=10)
    if not session_result.sessions:
        pytest.skip("当前账号没有可用于测试的私信会话")

    result = await authenticated_client.private_message.get_messages(
        session_id=session_result.sessions[0].session_id, size=10
    )
    assert result.messages is not None
    assert result.has_more in (0, 1)
