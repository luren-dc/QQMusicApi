import pytest


def pytest_addoption(parser):
    parser.addoption("--login", action="store_false", help="测试login函数")


@pytest.fixture
def test_login(request):
    if request.config.getoption("--login"):
        raise pytest.skip("使用'--login'测试登录函数")
