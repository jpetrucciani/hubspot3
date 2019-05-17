
hubspot3
========

.. image:: https://travis-ci.org/jpetrucciani/hubspot3.svg?branch=master
    :target: https://travis-ci.org/jpetrucciani/hubspot3


.. image:: https://badge.fury.io/py/hubspot3.svg
   :target: https://badge.fury.io/py/hubspot3
   :alt: PyPI version


.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/ambv/black
   :alt: Code style: black


.. image:: https://readthedocs.org/projects/hubspot3/badge/?version=latest
   :target: https://hubspot3.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status


.. image:: https://img.shields.io/badge/python-3.5+-blue.svg
   :target: https://www.python.org/downloads/release/python-350/
   :alt: Python 3.5+ supported


A python wrapper around HubSpot\'s APIs, *for python 3.5+*.

Built initially around hapipy, but heavily modified.

Check out the `documentation here <https://hubspot3.readthedocs.io/en/latest/>`_\ ! (thanks readthedocs)

Quick start
-----------

Installation
^^^^^^^^^^^^

.. code-block:: bash

   # install hubspot3
   pip install hubspot3

Basic Usage
^^^^^^^^^^^

.. code-block:: python

   from hubspot3 import Hubspot3

   API_KEY = "your-api-key"

   client = Hubspot3(api_key=API_KEY)

   # all of the clients are accessible as attributes of the main Hubspot3 Client
   contact = client.contacts.get_contact_by_email('testingapis@hubspot.com')
   contact_id = contact['vid']

   all_companies = client.companies.get_all()

   # new usage limit functionality - keep track of your API calls
   client.usage_limit
   # <Hubspot3UsageLimits: 28937/1000000 (0.028937%) [reset in 22157s, cached for 299s]>

   client.usage_limit.calls_remaining
   # 971063


Individual Clients
^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from hubspot3.companies import CompaniesClient

   API_KEY = "your-api-key"

   client = CompaniesClient(api_key=API_KEY)

   for company in client.get_all():
       print(company)

Passing Params
^^^^^^^^^^^^^^

.. code-block:: python

   import json
   from hubspot3.deals import DealsClient

   deal_id = "12345"
   API_KEY = "your_api_key"

   deals_client = DealsClient(api_key=API_KEY)

   params = {
       "includePropertyVersions": "true"
   }  # Note values are camelCase as they appear in the Hubspot Documentation!

   deal_data = deals_client.get(deal_id, params=params)
   print(json.dumps(deal_data))

Rate Limiting
-------------

Be aware that this uses the HubSpot API directly, so you are subject to all of the `guidelines that HubSpot has in place <https://developers.hubspot.com/apps/api_guidelines>`_\.

at the time of writing, HubSpot has the following limits in place for API requests:


* 10 requests per second
* 40,000 requests per day. This daily limit resets at midnight based on the time zone setting of the HubSpot account

Retrying API Calls
------------------

By default, hubspot3 will attempt to retry all API calls up to 2 times upon failure.

If you'd like to override this behavior, you can add a ``number_retries`` keyword argument to any Client constructor, or to individual API calls.


Extending the BaseClient - thanks `@Guysoft <https://github.com/guysoft>`_\ !
-------------------------------------------------------------------------------

Some of the APIs are not yet complete! If you\'d like to use an API that isn\'t yet in this repo, you can extend the BaseClient class!

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
           params = {}

           return self._call("pipelines", method="GET", params=params)

       def _get_path(self, subpath):
           return "deals/v{}/{}".format(
               self.options.get("version") or PIPELINES_API_VERSION, subpath
           )


   if __name__ == "__main__":
       API_KEY = "your_api_key"
       a = PipelineClient(api_key=API_KEY)
       print(json.dumps(a.get_pipelines()))

List of available clients
-------------------------

.. code-block:: yaml

   hubspot3/
     setup.py:             pip setup file

     hubspot3/
       __init__.py:          hubspot3 module
       base.py:              base hubspot client class
       blog.py:              hubspot blog api client
       broadcast.py:         hubspot broadcast api
       companies.py:         hubspot companies api
       contact_lists.py:     hubspot contact lists api
       contacts.py:          hubspot contacts api
       crm_associations.py:  hubspot crm_associations api
       crm_pipelines.py:     hubspot crm_pipelines api
       deals.py:             hubspot deals api
       engagements.py:       hubspot engagements api
       error.py:             hubspot3 error helpers
       forms.py:             hubspot forms api
       globals.py:           globals file for hubspot3
       keywords.py:          hubspot keywords api
       leads.py:             hubspot leads api
       logging_helper.py:    logging helper function
       owners.py:            hubspot owners api
       prospects.py:         hubspot prospects client
       settings.py:          hubspot settings api
       utils.py:             base utils for the hubspot3 library


Testing
-------

I'm currently working on rewriting many of the tests with `pytest <https://docs.pytest.org/en/latest/>`_\  to work against the public API and ensure that we get the correct type of mock data back. These tests are currently in a **very** early state - I'll be working soon to get them all built out.

.. code-block:: bash

   # run tests
   make
   # or
   make test_all
