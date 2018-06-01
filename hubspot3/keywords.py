"""
hubspot keywords api
"""
from hubspot3.base import BaseClient

KEYWORDS_API_VERSION = "v1"


class KeywordsClient(BaseClient):
    """allows access to the keywords api"""

    def _get_path(self, subpath):
        return "keywords/{}/{}".format(KEYWORDS_API_VERSION, subpath)

    # Contains both list of keywords and metadata
    def get_keywords_info(self, **options):
        return self._call("keywords", **options)

    # *Only* returns the list of keywords, does not include additional metadata
    def get_keywords(self, **options):
        return self._call("keywords", **options)["keywords"]

    def get_keyword(self, keyword_guid, **options):
        return self._call("keywords/{}".format(keyword_guid, **options))

    def add_keyword(self, keyword, **options):
        return self._call(
            "keywords", data=dict(keyword=str(keyword)), method="PUT", **options
        )

    def add_keywords(self, keywords, **options):
        data = []
        for keyword in keywords:
            if keyword != "":
                if isinstance(keyword, dict):
                    data.append(keyword)
                elif isinstance(keyword, str):
                    data.append(dict(keyword=str(keyword)))
        return self._call("keywords", data=data, method="PUT", **options)["keywords"]

    def delete_keyword(self, keyword_guid, **options):
        return self._call(
            "keywords/{}".format(keyword_guid), method="DELETE", **options
        )
