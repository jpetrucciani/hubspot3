"""
Tests for the Hubspot3 main module.
"""
import io
import pytest
from contextlib import contextmanager
from json import JSONDecodeError
from unittest.mock import Mock, mock_open, patch
from hubspot3.__main__ import (
    ClientCLIWrapper,
    get_config_from_file,
    Hubspot3CLIWrapper,
    split_args,
)
from hubspot3.base import BaseClient


@contextmanager
def does_not_raise():
    yield


@pytest.fixture
def client_wrapper():
    client = Mock(spec=BaseClient)
    return ClientCLIWrapper(client)


@pytest.fixture
def cli_wrapper():
    return Hubspot3CLIWrapper()


@pytest.mark.parametrize(
    "value, expectation",
    [
        ("", pytest.raises(JSONDecodeError)),
        ("[]", pytest.raises(RuntimeError)),
        ("{}", does_not_raise()),
        ('{"api-key": "xxxxxx-xxxxxx-xxxx-xxx"}', does_not_raise()),
    ],
)
def test_get_config_from_file(value, expectation):
    with patch("hubspot3.__main__.open", mock_open(read_data=value)):
        with expectation:
            get_config_from_file("test.json")


@pytest.mark.parametrize(
    "args, expectation",
    [
        (["hubspot3"], ([], [], [])),
        (["hubspot3", "--help"], ([], [], ["--help"])),
        (["hubspot3", "--", "--help"], ([], [], ["--help"])),
        (
            ["hubspot3", "--timeout", "10", "--api-key", "xxx-xxx", "contacts"],
            (["--timeout", "10", "--api-key", "xxx-xxx"], ["contacts"], []),
        ),
        (
            ["hubspot3", "--api-key", "xxx-xxx", "contacts", "get-all"],
            (["--api-key", "xxx-xxx"], ["contacts", "get-all"], []),
        ),
        (
            ["hubspot3", "contacts", "get-all", "--", "--help"],
            ([], ["contacts", "get-all"], ["--help"]),
        ),
        (
            ["hubspot3", "--timeout=10", "--api-key=xxx-xxx", "contacts"],
            (["--timeout=10", "--api-key=xxx-xxx"], ["contacts"], []),
        ),
    ],
)
def test_split_args(args, expectation):
    with patch("hubspot3.__main__.sys.argv", args):
        assert split_args() == expectation


class TestHubspot3CLIWrapper:
    @pytest.mark.parametrize(
        "kwargs, expected_kwargs, config",
        [
            ({}, {"disable_auth": True}, None),
            ({"config": "config.json"}, {}, {}),
            ({"api_key": "xxx-xxx"}, {"api_key": "xxx-xxx"}, {}),
            (
                {"config": "config.json", "api_key": "xxx-xxx"},
                {"api_key": "xxx-xxx"},
                {"api_key": "123-456"},
            ),
        ],
    )
    @patch("hubspot3.__main__.Hubspot3CLIWrapper._discover_clients")
    @patch("hubspot3.__main__.get_config_from_file")
    @patch("hubspot3.__main__.Hubspot3")
    def test_constructor(
        self,
        mock_hubspot3,
        mock_get_config_from_file,
        mock_discover_clients,
        kwargs,
        expected_kwargs,
        config,
    ):
        clients = {"client_a": Mock(spec=BaseClient), "client_b": Mock(spec=BaseClient)}
        mock_get_config_from_file.return_value = config
        mock_discover_clients.return_value = clients
        wrapper = Hubspot3CLIWrapper(**kwargs)
        assert mock_discover_clients.called
        for name in clients.keys():
            assert hasattr(wrapper, name)
        mock_hubspot3.assert_called_with(**expected_kwargs)
        if "config" in kwargs:
            mock_get_config_from_file.assert_called_with(kwargs["config"])

    @pytest.mark.parametrize(
        "properties, ignored_properties, expectation",
        [
            ({}, [], []),
            ({"client_a": property(lambda x: Mock(spec=BaseClient))}, [], ["client_a"]),
            (
                {
                    "client_a": property(lambda x: Mock(spec=BaseClient)),
                    "client_b": property(lambda x: Mock(spec=BaseClient)),
                },
                ["client_a"],
                ["client_b"],
            ),
            ({"client_a": property(lambda x: x)}, [], []),
            (
                {
                    "client_a": property(lambda x: Mock(spec=BaseClient)),
                    "_client_b": property(lambda x: Mock(spec=BaseClient)),
                    "__client_c": property(lambda x: Mock(spec=BaseClient)),
                },
                [],
                ["client_a"],
            ),
        ],
    )
    def test_discover_clients(
        self, properties, ignored_properties, expectation, cli_wrapper
    ):
        class Hubspot3:
            pass

        for name, value in properties.items():
            setattr(Hubspot3, name, value)
        cli_wrapper.IGNORED_PROPERTIES = ignored_properties
        clients = cli_wrapper._discover_clients(Hubspot3())
        assert list(clients) == expectation


class TestClientCLIWrapper:
    @patch("hubspot3.__main__.ClientCLIWrapper._discover_methods")
    @patch("hubspot3.__main__.ClientCLIWrapper._build_method_wrapper")
    def test_constructor(self, mock_build_method_wrapper, mock_discover_methods):
        class APIClient:
            pass

        methods = {"method_a": lambda x: x, "method_b": lambda x: x}
        mock_discover_methods.return_value = methods
        mock_build_method_wrapper.return_value = "test"
        client = APIClient()
        wrapper = ClientCLIWrapper(client)
        mock_discover_methods.assert_called_with(client)
        assert wrapper._client_name == "APIClient"
        assert wrapper._methods == methods
        for fn_name, fn in methods.items():
            assert getattr(wrapper, fn_name) == "test"

    @pytest.mark.parametrize(
        "args, kwargs, expectation, stdin_value",
        [
            ([], {}, ([], {}), None),
            (
                [],
                {"data": "__stdin__"},
                ([], {"data": '{"firstname": "Test"}'}),
                '{"firstname": "Test"}',
            ),
            (
                ["__stdin__"],
                {},
                (['{"firstname": "Test"}'], {}),
                '{"firstname": "Test"}',
            ),
        ],
    )
    @patch("hubspot3.__main__.sys.stdin", Mock(new_callable=io.StringIO))
    @patch("hubspot3.__main__.json.load")
    def test_replace_stdin_token(
        self, mock_load, client_wrapper, args, kwargs, expectation, stdin_value
    ):
        mock_load.return_value = stdin_value
        value = client_wrapper._replace_stdin_token(*args, **kwargs)
        assert value == expectation
        if stdin_value:
            assert mock_load.called

    @pytest.mark.parametrize(
        "methods, ignored_methods, expectation",
        [
            ({}, [], []),
            ({"a": 1337}, [], []),
            ({"_a": 1337}, [], []),
            ({"_method_a": lambda x: x}, [], []),
            ({"__method_a": lambda x: x}, [], []),
            ({"__method_a": lambda x: x, "_method_b": lambda x: x}, [], []),
            (
                {"_method_a": lambda x: x, "method_b": lambda x: x, "c": 1337},
                [],
                ["method_b"],
            ),
            (
                {"method_a": lambda x: x, "method_b": lambda x: x},
                ["method_b"],
                ["method_a"],
            ),
        ],
    )
    def test_discover_methods(
        self, client_wrapper, methods, ignored_methods, expectation
    ):
        class APIClient:
            pass

        client_wrapper.IGNORED_METHODS = {
            APIClient: method for method in ignored_methods
        }
        for name, method in methods.items():
            setattr(APIClient, name, method)
        client = APIClient()
        discovered_methods = client_wrapper._discover_methods(client)
        assert list(discovered_methods) == expectation

    @pytest.mark.parametrize(
        "result, json_dumps, expectation",
        [
            (
                b'{"firstname": "Name"}',
                Mock(side_effect=Exception),
                b'{"firstname": "Name"}',
            ),
            (
                b'{"firstname": "Name"}',
                Mock(return_value={"firstname": "Name"}),
                {"firstname": "Name"},
            ),
            (
                {"firstname": "Name"},
                Mock(return_value={"firstname": "Name"}),
                {"firstname": "Name"},
            ),
        ],
    )
    @patch("hubspot3.__main__.ClientCLIWrapper._replace_stdin_token")
    @patch("hubspot3.__main__.ClientCLIWrapper._build_wrapper_doc")
    def test_build_method_wrapper(
        self,
        mock_build_wrapper_doc,
        mock_replace_stdin_token,
        client_wrapper,
        result,
        json_dumps,
        expectation,
    ):
        def method():
            return result

        mock_replace_stdin_token.return_value = ([], {})
        mock_build_wrapper_doc.return_value = "Test documentation"
        with patch("hubspot3.__main__.json.dumps", json_dumps):
            wrapped = client_wrapper._build_method_wrapper(method)
            wrapped()
        assert mock_replace_stdin_token.called
        if isinstance(result, bytes):
            result = result.decode("utf-8")
        json_dumps.assert_called_with(result)
        assert wrapped.__doc__ == "Test documentation"
