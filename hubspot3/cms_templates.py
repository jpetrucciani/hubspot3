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
        return f"content/api/v{TEMPLATES_API_VERSION}/templates/{subpath}"

    def get_templates(self, **options):
        return self._call("", **options)

    def get_template_info(self, template_id: str, **options):
        return self._call(f"{template_id}", **options)

    def get_template_buffer(self, template_id: str, **options):
        return self._call(f"{template_id}/buffer", **options)

    def get_template_has_buffered_changes(self, template_id: str, **options):
        return self._call(f"{template_id}/has_buffered_changes", **options)

    def get_template_versions(self, template_id: str, **options):
        return self._call(f"{template_id}/versions", **options)

    def get_template_version_info(self, template_id: str, version_id: str, **options):
        return self._call(f"{template_id}/versions/{version_id}", **options)
