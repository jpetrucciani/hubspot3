"""
hubspot settings api
"""
from hubspot3.base import (
    BaseClient
)
from hubspot3.error import (
    HubspotError
)


SETTINGS_API_VERSION = 'v1'


class SettingsClient(BaseClient):
    """
    Basic Python client for the HubSpot Settings API.

    Use this to read settings for a given API key, as well as update a setting.

    Reference docs: http://docs.hubapi.com/wiki/Settings_API

    Comments, questions, etc: http://docs.hubapi.com/wiki/Discussion_Group
    """
    def _get_path(self, subpath):
        return 'settings/{}/{}'.format(SETTINGS_API_VERSION, subpath)

    def get_settings(self, **options):
        """Returns the settings we know about for this API key."""
        return self._call('settings', **options)

    def get_setting(self, name, **options):
        """Returns the specific requested setting name, if found."""
        params = {'name': name}
        return self._call('settings', params=params, **options)

    def update_setting(self, data, **options):
        """Updates a specific setting for this API key."""
        params = {}
        if data['name']:
            params['name'] = data['name']
        if data['value']:
            params['value'] = data['value']

        return self._call('settings', params=params, data=data, method='POST', **options)

    def delete_setting(self, name, **options):
        """"Deletes" a specific setting by emptying out its value."""
        params = {}
        if name:
            params['name'] = name
        else:
            raise HubspotError('Setting name required.')
        return self._call('settings', params=params, method='DELETE', **options)
