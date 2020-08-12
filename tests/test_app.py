import pytest
from continuum_deployer.app import Hello


def test_app():
    name = "boilerplate"
    hello_instance = Hello(name=name)
    hello_instance.say()
    assert name == hello_instance.get_name()


def test_app_failed():
    name = "boilerplate"
    hello_instance = Hello(name="not boilerplate")
    assert not name == hello_instance.get_name()
