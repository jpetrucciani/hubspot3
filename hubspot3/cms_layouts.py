"""
hubspot cms_layout api client
"""

from hubspot3.base import BaseClient


LAYOUTS_API_VERSION = "2"


class CMSLayoutsClient(BaseClient):
    """
    provides a client for accessing hubspot layout info
    """

    def _get_path(self, subpath: str) -> str:
        return f"content/api/v{LAYOUTS_API_VERSION}/layouts/{subpath}"

    def get_layouts(self, **options):
        return self._call("", **options)

    def get_layout_info(self, layout_id: str, **options):
        return self._call(f"{layout_id}", **options)

    def get_layout_buffer(self, layout_id: str, **options):
        return self._call(f"{layout_id}/buffer", **options)

    def get_layout_has_buffered_changes(self, layout_id: str, **options):
        return self._call(f"{layout_id}/has_buffered_changes", **options)

    def get_layout_versions(self, layout_id: str, **options):
        return self._call(f"{layout_id}/versions", **options)

    def get_layout_version_info(self, layout_id: str, version_id: str, **options):
        return self._call(f"{layout_id}/versions/{version_id}", **options)
