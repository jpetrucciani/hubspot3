"""Commandline entry for the Hubspot client."""
import json
import sys
from functools import wraps

from fire import Fire
from fire.core import _Fire
from fire.parser import SeparateFlagArgs
from hubspot3 import Hubspot3
from hubspot3.base import BaseClient


class Hubspot3CLIWrapper(object):

    IGNORED_ATTRS = ('me', 'usage_limits')

    def __init__(self, **kwargs):

        config_file = kwargs.pop('config', None)
        if config_file is not None:
            with open(config_file, 'r', encoding='utf-8') as fp:
                config = json.load(fp)
            if not isinstance(config, dict):
                raise RuntimeError('Config file content must be an object, got {} instead '.
                                   format(type(config).__name__))
            kwargs = dict(config, **kwargs)

        hubspot3 = Hubspot3(**kwargs)
        self._clients = self._find_clients(hubspot3)
        for attr, client in self._clients.items():
            setattr(self, attr, ClientCLIWrapper(client))

    def __dir__(self):
        return self._clients

    def _find_clients(self, hubspot3):
        clients = {}
        for attr in dir(Hubspot3):
            if attr.startswith('_') or attr in self.IGNORED_ATTRS or not isinstance(getattr(Hubspot3, attr), property):
                continue
            client = getattr(hubspot3, attr)
            if isinstance(client, BaseClient):
                clients[attr] = client
        return clients


class ClientCLIWrapper(object):

    def __init__(self, client):
        self._methods = self._find_methods(client)
        for attr, method in self._methods.items():
            setattr(self, attr, self._build_method_wrapper(method))

    def __dir__(self):
        return self._methods

    def _find_methods(self, client):
        methods = {}
        for attr in dir(client):
            if attr.startswith('_'):
                continue
            method = getattr(client, attr)
            if hasattr(method, '__self__'):
                methods[attr] = method
        return methods

    def _build_method_wrapper(self, method):
        @wraps(method)
        def wrapper(**kwargs):

            stdin_keys = [key for key, value in kwargs.items() if '<stdin>' == value]
            if stdin_keys:
                value = json.load(sys.stdin)
                for key in stdin_keys:
                    kwargs[key] = value

            result = method(**kwargs)
            try:
                result = json.dumps(result)
            except Exception:
                pass
            print(result)
        return wrapper


def main():
    args, fire_args = SeparateFlagArgs(sys.argv[1:])
    index = 0
    while index < len(args):
        arg = args[index]
        if arg.startswith('--'):
            if '=' not in arg:
                index += 1
            index += 1
        else:
            break
    client_args, call_args = args[:index], args[index:]
    (call_args or client_args).extend(['--'] + fire_args)
    if call_args:
        component_trace = _Fire(Hubspot3CLIWrapper, client_args, {})
        wrapper = component_trace.GetResult()
        Fire(wrapper, call_args)
    else:
        Fire(Hubspot3CLIWrapper, client_args)


if __name__ == '__main__':
    main()
