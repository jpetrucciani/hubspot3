"""Commandline entry for the Hubspot client."""
import json
import sys
import types
from functools import wraps
from typing import Callable, Dict, List, Tuple

from fire.core import Fire as fire, _Fire as fire_execute
from fire.helputils import UsageString as build_usage_string
from fire.parser import SeparateFlagArgs as separate_flag_args
from hubspot3 import Hubspot3
from hubspot3.base import BaseClient
from hubspot3.leads import LeadsClient


def get_config_from_file(filename):
    """Return the content of a JSON config file as a dictionary."""
    with open(filename, 'r', encoding='utf-8') as fp:
        config = json.load(fp)
    if not isinstance(config, dict):
        raise RuntimeError('Config file content must be an object, got "{}" instead.'.format(type(config).__name__))
    return config


class Hubspot3CLIWrapper(object):
    __doc__ = """
        Hubspot3 CLI
        
        To get a list of supported operations, call this CLI without the "--help" option.
        
        The API client can be configured by providing options BEFORE specifying the operation to execute. KWARGS are:
        [--config CONFIG_FILE_PATH] {}
    """.format(build_usage_string(Hubspot3).split('\n')[-1])

    # Properties to ignore during discovery. The "me" property must be ignored
    # as it would already perform an API request while being discovered and the
    # "usage_limits" property does not contain an API.
    # Extend this tuple if more properties that aren't API clients are added to
    # the Hubspot3 class.
    IGNORED_PROPERTIES = ('me', 'usage_limits')

    def __init__(self, **kwargs):
        # If no arguments were supplied at all, the desired outcome is likely
        # the list of operations/clients. Therefore disable authentication to
        # stop the Hubspot3 initializer from raising an exception since there
        # is neither an API key nor an access token.
        if not kwargs:
            kwargs['disable_auth'] = True

        # If a config file was specified, read its settings and merge the CLI
        # options into them.
        config_file = kwargs.pop('config', None)
        if config_file is not None:
            config = get_config_from_file(config_file)
            kwargs = dict(config, **kwargs)

        # Initialize the main client, discover all sub-clients and set them as
        # attributes on this wrapper so Fire can discover them.
        hubspot3 = Hubspot3(**kwargs)
        self._clients = self._discover_clients(hubspot3)
        for attr, client in self._clients.items():
            setattr(self, attr, ClientCLIWrapper(client))

    def __dir__(self):
        return self._clients  # Let Fire only discover the client attributes.

    def __str__(self):
        return 'Hubspot3 CLI'

    def _discover_clients(self, hubspot3: Hubspot3) -> Dict[str, BaseClient]:
        """Find all client instance properties on the given Hubspot3 object."""
        clients = {}
        for attr in dir(hubspot3.__class__):
            # Find properties by searching the class first - that way, a call
            # to getattr doesn't run the properties code on the object.
            if (attr.startswith('_') or attr in self.IGNORED_PROPERTIES or
                    not isinstance(getattr(hubspot3.__class__, attr), property)):
                continue
            client = getattr(hubspot3, attr)
            if isinstance(client, BaseClient):
                clients[attr] = client
        return clients


class ClientCLIWrapper(object):
    __doc__ = Hubspot3CLIWrapper.__doc__

    # Mapping (client class to attribute names) to define methods that should
    # be ignored during method discovery.
    # Extend this mapping if more methods that aren't API methods are added to
    # a client class.
    IGNORED_METHODS = {
        LeadsClient: ('camelcase_search_options',),
    }
    STDIN_TOKEN = '__stdin__'  # Argument value to trigger stdin parsing.

    def __init__(self, client: BaseClient):
        self._client_name = client.__class__.__name__
        # Discover all API methods and set them as attributes on this wrapper
        # so Fire can discover them.
        self._methods = self._discover_methods(client)
        for attr, method in self._methods.items():
            setattr(self, attr, self._build_method_wrapper(method))

    def __dir__(self):
        return self._methods  # Let Fire only discover the API methods.

    def __str__(self):
        return 'Hubspot3 {} CLI'.format(self._client_name)

    def _discover_methods(self, client: BaseClient) -> Dict[str, types.MethodType]:
        """Find all API methods on the given client object."""
        methods = {}
        for attr in dir(client):
            if attr.startswith('_') or attr in self.IGNORED_METHODS.get(client.__class__, ()):
                continue
            method = getattr(client, attr)
            if isinstance(method, types.MethodType):
                methods[attr] = method
        return methods

    def _build_method_wrapper(self, method: types.MethodType) -> Callable:
        """Build a wrapper function around the given API method."""
        @wraps(method)
        def wrapper(*args, **kwargs):
            # Replace the stdin token with the actual stdin value and call the
            # original API method.
            args, kwargs = self._replace_stdin_token(*args, **kwargs)
            result = method(*args, **kwargs)

            # Try to ensure to always write JSON to stdout, but don't hide any
            # result either if it can't be JSON-encoded.
            if isinstance(result, bytes):
                result = result.decode('utf-8')
            try:
                result = json.dumps(result)
            except Exception:
                pass
            print(result)
        wrapper.__doc__ = self._build_wrapper_doc(method)
        return wrapper

    def _build_wrapper_doc(self, method: types.MethodType) -> str:
        """Build a helpful docstring for a wrapped API method."""
        return '\n'.join((
            method.__doc__ or '',
            '',
            'Supported ARGS/KWARGS are:',
            build_usage_string(method),
            '',
            'The token "{}" may be used as an argument value, which will cause JSON data to be read from stdin and '
            'used as the actual value for the argument.'.format(self.STDIN_TOKEN),
        ))

    def _replace_stdin_token(self, *args, **kwargs) -> Tuple[List, Dict]:
        """
        Replace the values of all given arguments with the JSON-parsed value
        from stdin if their current value is the STDIN_TOKEN.
        """
        stdin_indices = [index for index, value in enumerate(args) if value == self.STDIN_TOKEN]
        stdin_keys = [key for key, value in kwargs.items() if value == self.STDIN_TOKEN]
        if stdin_indices or stdin_keys:
            value = json.load(sys.stdin)
            args = list(args)
            for index in stdin_indices:
                args[index] = value
            for key in stdin_keys:
                kwargs[key] = value
        return args, kwargs


def split_args() -> Tuple[List, List, List]:
    """
    Split system args into three group of argument lists.

    This method will separate all system args in client, API call and fire args
    so that is much easier to instantiate them independently with their own
    arguments.
    """
    args = sys.argv[1:]
    if args == ['--help']:
        # If the user only called the CLI with "--help", pass it through as an
        # argument for Fire to invoke its help functionality.
        return [], [], args

    # Use a Fire function to split away the Fire arguments.
    args, fire_args = separate_flag_args(args)

    # Search for an argument that represents the sub-client that should be
    # used. Since the CLI arguments have a fixed pattern (client options,
    # sub-client name, method name, method options), this must be the first
    # argument that isn't a named client option argument.
    api_index = 0
    while api_index < len(args):
        arg = args[api_index]
        # Named options can be passed as "--key=value" or "--key value", so the
        # next argument to look at is either the next argument or the one after
        # that, respectively.
        if arg.startswith('--'):
            if '=' not in arg:
                api_index += 1
            api_index += 1
        else:
            break
    client_args, call_args = args[:api_index], args[api_index:]
    return client_args, call_args, fire_args


def main():
    """
    Main routine.

    Split the execution up into two Fire calls: one that creates the main
    Hubspot3CLIWrapper instance and one that works on this instance. That way,
    the argument separator is not required and sensible details like the API
    key are not printed out.
    """
    client_args, call_args, fire_args = split_args()

    if fire_args:
        # If there are arguments for an actual API method call, append the Fire
        # arguments to that second call. Otherwise, append them to the first
        # call as there won't be a second one.
        (call_args or client_args).extend(['--'] + fire_args)
    if call_args:
        # Use the non-printing Fire routine for the first call as only the
        # result of the second, actual API call should be printed.
        component_trace = fire_execute(Hubspot3CLIWrapper, client_args, {}, __package__)
        wrapper = component_trace.GetResult()
        fire(wrapper, call_args)
    else:
        fire(Hubspot3CLIWrapper, client_args, __package__)


if __name__ == '__main__':
    main()
