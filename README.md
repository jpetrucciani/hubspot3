# hubspot3

A python wrapper around HubSpot\'s APIs, for python 3.

Built initially around hapipy, but heavily modified.

## Quick start

Here is a basic usage

```python
from hubspot3.companies import CompaniesClient
API = "your-api"
client = CompaniesClient(api_key=API)
for company in client.get_all():
    print(company)
```

## List of available clients

```yaml
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
```
