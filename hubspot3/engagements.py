"""
hubspot engagements api
"""
from hubspot3.base import BaseClient
from hubspot3.utils import clean_result, get_log


ENGAGEMENTS_API_VERSION = "1"


class EngagementsClient(BaseClient):
    """
    The hubspot3 Engagements client uses the _make_request method to call the API
    for data.  It returns a python object translated from the json returned
    """

    def __init__(self, *args, **kwargs):
        super(EngagementsClient, self).__init__(*args, **kwargs)
        self.log = get_log("hubspot3.engagements")

    def _get_path(self, subpath):
        return "engagements/v{}/{}".format(
            self.options.get("version") or ENGAGEMENTS_API_VERSION, subpath
        )

    def get(self, engagement_id, **options):
        """Get a HubSpot engagement."""
        return self._call(
            "engagements/{}".format(engagement_id), method="GET", **options
        )

    def get_associated(self, object_type, object_id, **options):
        """
        get all engagements associated with the given object
        :param object_type: type of object to get associations on [CONTACT, COMPANY, DEAL]
        :param object_id: ID of the object to get associations on
        """
        finished = False
        output = []
        query_limit = 100  # Max value according to docs
        offset = 0
        while not finished:
            print(offset)
            batch = self._call(
                "engagements/associated/{}/{}/paged".format(object_type, object_id),
                method="GET",
                params={"limit": query_limit, "offset": offset},
                **options
            )
            print(len(batch["results"]))
            output.extend(batch["results"])
            finished = not batch["hasMore"]
            offset = batch["offset"]

        return output

    def create(self, data=None, **options):
        data = data or {}
        return self._call("engagements", data=data, method="POST", **options)

    def update(self, key, data=None, **options):
        data = data or {}
        return self._call(
            "engagements/{}".format(key), data=data, method="PUT", **options
        )

    def get_all(self, limit=-1, **options):
        engagement_generator = self.get_all_as_generator(limit=limit,
                                                         **options)
        return list(engagement_generator)

    def get_all_as_generator(self, limit=-1, **options):
        """get all engagements"""
        finished = False
        query_limit = 250  # Max value according to docs
        limited = limit > 0
        if limited and limit < query_limit:
            query_limit = limit
        offset = 0
        engagement_counter = 0
        while not finished:
            batch = self._call(
                "engagements/paged",
                method="GET",
                params={"limit": query_limit, "offset": offset},
                **options
            )

            engagements = batch["results"]

            engagement_counter += len(engagements)
            reached_limit = limited and engagement_counter >= limit

            if reached_limit:
                cutoff = len(engagements) - (engagement_counter - limit)
                engagements = engagements[:cutoff]

            finished = not batch["hasMore"] or reached_limit
            offset = batch["offset"]

            yield from engagements

    def get_recently_modified(self, start_date: int, end_date: int, **options):
        """Get recently modified engagements."""
        finished = False
        engagements = []
        query_limit = 100  # Max value according to docs
        offset = 0

        while not finished:
            batch = self._call(
                "engagements/recent/modified",
                method="GET",
                params={"limit": query_limit, "offset": offset, "since": start_date},
                **options
            )
            engagements.extend(batch["results"])
            finished = not batch["hasMore"]
            offset = batch["offset"]
            engagements = clean_result("engagements", engagements, start_date, end_date)

            yield from engagements

    def count_recently_modified_engagements(self, since: int):
        """check limit of request."""
        query_limit = 100  # Max value according to docs
        offset = 0

        batch = self._call(
            "engagements/recent/modified",
            method="GET",
            params={"limit": query_limit, "offset": offset, "since": start_date}
        )
        total = batch["total"]
        return total
