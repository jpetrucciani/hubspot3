"""
hubspot cms_files api
"""
from typing import Dict
from hubspot3.base import BaseClient


CMS_FILES_API_VERSION = "2"


class CMSFilesClient(BaseClient):
    """
    provides a client for accessing cms files
    """

    def _get_path(self, subpath: str) -> str:
        return f"filemanager/api/v{CMS_FILES_API_VERSION}/files/{subpath}"

    def get_file_meta_data(self, file_id: int, **options) -> Dict:
        return self._call(f"{file_id}", **options)
