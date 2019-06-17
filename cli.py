"""Commandline entry for the Hubspot client."""

from functools import wraps
import json

from fire import Fire
from hubspot3 import Hubspot3
from hubspot3.base import BaseClient


class Hubspot3CLIWrapper(object):

    IGNORED_ATTRS = ('me', 'usage_limits')

    def __init__(self, **kwargs):
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
            result = method(**kwargs)
            try:
                result = json.dumps(result)
            except Exception:
                pass
            print(result)
        return wrapper


if __name__ == '__main__':
    Fire(Hubspot3CLIWrapper)
