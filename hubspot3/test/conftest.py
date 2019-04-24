"""
configure pytest
"""
import pytest


@pytest.fixture(scope="session", autouse=True)
def before_all(request):
    """test setup"""
    request.addfinalizer(after_all)


def after_all():
    """tear down"""
    pass
