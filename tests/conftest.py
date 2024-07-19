import pytest


def pytest_addoption(parser):
    parser.addoption("--test-login", action="store_false", help="Use this option to test login API")


@pytest.fixture
def is_test_login(request):
    if request.config.getoption("--test-login"):
        pytest.skip("skip test login API")
