
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


A python wrapper around HubSpot\'s APIs, *for python 3*.

Built initially around hapipy, but heavily modified.

Check out the `documentation here <https://hubspot3.readthedocs.io/en/latest/>`_\ ! (thanks readthedocs)

Quick start
-----------

Installation
^^^^^^^^^^^^

.. code-block:: bash

   # on ubuntu you may need this apt package:
   sudo apt-get install libcurl4-openssl-dev

   # install hubspot3
   pip install hubspot3

Basic Usage
^^^^^^^^^^^

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

Be aware that this uses the HubSpot API directly, so you are subject to all of the guidelines that HubSpot has in place:
https://developers.hubspot.com/apps/api_guidelines

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

       mixins/
         __init__.py:          extra functionalities for hubspot3
         threading.py:         allow threaded execution of hubspot api calls

       test/
         __init__.py:          no documentation found
         helper.py:            no documentation found
         logger.py:            no documentation found
         test_base.py:         no documentation found
         test_broadcast.py:    no documentation found
         test_error.py:        no documentation found
         test_keywords.py:     no documentation found
         test_leads.py:        no documentation found
         test_settings.py:     no documentation found
