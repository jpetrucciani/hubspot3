"""
hubspot cms_templates api client
"""
from hubspot3.base import BaseClient


TEMPLATES_API_VERSION = "2"


class CMSTemplatesClient(BaseClient):
    """
    provides a client for accessing hubspot template info
    """

    def _get_path(self, subpath: str) -> str:
        return "content/api/v{}/templates/{}".format(TEMPLATES_API_VERSION, subpath)

    def get_templates(self, **options):
        return self._call("", **options)

    def get_template_info(self, template_id: str, **options):
        return self._call("{}".format(template_id), **options)

    def get_template_buffer(self, template_id: str, **options):
        return self._call("{}/buffer".format(template_id), **options)

    def get_template_has_buffered_changes(self, template_id: str, **options):
        return self._call("{}/has_buffered_changes".format(template_id), **options)

    def get_template_versions(self, template_id: str, **options):
        return self._call("{}/versions".format(template_id), **options)

    def get_template_version_info(self, template_id: str, version_id: str, **options):
        return self._call("{}/versions/{}".format(template_id, version_id), **options)
