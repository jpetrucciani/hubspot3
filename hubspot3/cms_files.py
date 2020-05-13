"""
hubspot cms_files api
"""
from hubspot3.base import BaseClient


CMS_FILES_API_VERSION = "2"


class CMSFilesClient(BaseClient):
    """
    provides a client for accessing cms files
    """

    def _get_path(self, subpath: str) -> str:
        return "filemanager/api/v{}/files/{}".format(CMS_FILES_API_VERSION, subpath)

    def get_file_meta_data(self, file_id: int, **options):
        return self._call("{}".format(file_id), **options)
