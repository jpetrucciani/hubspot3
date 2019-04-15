.. _extending:

Extending
==========

Some of the APIs are not yet complete!

If you'd like to use an API that isn't yet in this repo, you can extend the BaseClient class! Also, feel free to make a PR if you think it would help others!


Extending from the BaseClient
-----------------------------

The following code block shows an example (provided by `guysoft <https://github.com/guysoft>`_)

.. code-block:: python

    import json
    from hubspot3.base import BaseClient


    PIPELINES_API_VERSION = "1"


    class PipelineClient(BaseClient):
        """
        Lets you extend to non-existing clients, this example extends pipelines
        """

        def __init__(self, *args, **kwargs):
            super(PipelineClient, self).__init__(*args, **kwargs)

        def get_pipelines(self, **options):
            params = {**options}  # unpack options as params for the api call

            return self._call("pipelines", method="GET", params=params)

        def _get_path(self, subpath):
            return "deals/v{}/{}".format(
                self.options.get("version") or PIPELINES_API_VERSION, subpath
            )


    if __name__ == "__main__":
        API_KEY = "your_api_key"
        a = PipelineClient(api_key=API_KEY)
        print(json.dumps(a.get_pipelines()))


Working with Pagination
-----------------------

Pagination can be tricky with how the hubspot API is set up.

Below is an example of how to deal with pagination from the DealsClient included in this library, specifically to get x number of recently created deals.

.. code-block:: python

    def get_recently_created(
        self, limit=100, offset=0, since=None, include_versions=False, **options
    ):
        """
        get recently created deals
        up to the last 30 days or the 10k most recently created records

        since: must be a UNIX formatted timestamp in milliseconds
        """
        finished = False
        output = []
        query_limit = 100  # max according to the docs

        while not finished:
            params = {
                "count": query_limit,
                "offset": offset,
                "includePropertyVersions": include_versions,
            }
            if since:
                params["since"] = since
            batch = self._call(
                "deal/recent/created",
                method="GET",
                params=params,
                doseq=True,
                **options
            )
            output.extend(
                [
                    prettify(deal, id_key="dealId")
                    for deal in batch["results"]
                    if not deal["isDeleted"]
                ]
            )
            finished = not batch["hasMore"] or len(output) >= limit
            offset = batch["offset"]

        return output[:limit]
