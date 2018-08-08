.. _quickstart:

Quickstart
==========

This document presents a brief, high-level overview of hubspot3's primary features.

hubspot3 is a python wrapper around HubSpot's APIs, for python 3.

.. note::
    Be aware that this uses the HubSpot API directly, so you are subject to all of the `guidelines that HubSpot has in place <https://developers.hubspot.com/apps/api_guidelines>`_.

At the time of writing, HubSpot has the following limits in place for API requests:

- 10 requests per second
- 40,000 requests per day. This daily limit resets at midnight based on the time zone setting of the HubSpot account

Installation
------------

.. code-block:: bash

    # on ubuntu you may need this apt package:
    sudo apt-get install libcurl4-openssl-dev

    # install hubspot3
    pip install hubspot3


Basic Usage
-----------

.. code-block:: python

    from hubspot3.companies import CompaniesClient

    API_KEY = "your-api-key"

    client = CompaniesClient(api_key=API_KEY)

    for company in client.get_all():
        print(company)


Passing Params
--------------

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
