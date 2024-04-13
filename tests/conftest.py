import pytest


def pytest_addoption(parser):
    parser.addoption("--login", action="store_false", help="测试登录Api")


@pytest.fixture
def is_test_login(request):
    if request.config.getoption("--login"):
        pytest.skip("使用'--login'参数测试登录Api")
