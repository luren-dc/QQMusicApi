import httpx
import pytest

from qqmusic_api.utils.network import ApiRequest, RequestGroup

pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest.fixture
def mock_client(monkeypatch):
    async def mock_post(*args, **kwargs):
        class MockResponse:
            def __init__(self, json_data, status_code=200):
                self.json_data = json_data
                self.status_code = status_code
                self.content = json_data

            def json(self):
                return self.json_data

            def raise_for_status(self):
                pass

        data = kwargs.get("json", {})
        data.pop("comm", None)
        return MockResponse({key: {"code": 0, "data": {"result": "success"}} for key in data.keys()})

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)


async def test_api_request(mock_client):
    api = ApiRequest(
        module="music.smartboxCgi.SmartBoxCgi",
        method="GetSmartBoxResult",
        params={"query": "test"},
    )
    response = await api()
    assert response == {"result": "success"}


async def test_request_group(mock_client):
    group = RequestGroup()
    api = ApiRequest(
        module="music.smartboxCgi.SmartBoxCgi",
        method="GetSmartBoxResult",
        params={"query": "test"},
    )
    group.add_request(api)
    group.add_request(api)
    results = await group.execute()
    assert results == [{"result": "success"}, {"result": "success"}]
