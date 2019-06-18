.. commandline:

Commandline
===========

The hubspot3 client comes with an optional commandline interface that makes it easy to use the client's features without
necessarily importing it within a Python project.

Installation
------------

To use the commandline interface you will have to install an additional Python requirement:

.. code-block:: bash

    pip install hubspot3[cli]

Usage
-----

After the installation you can use the client with the ``hubspot3`` command, e.g. to display the help:

.. code-block:: bash

    hubspot3 --help

This will display all arguments for the general usage of the commandline client, like the API key (or a config file,
see below). Please take a look into the constructor of the ``hubspot3.Hubspot3`` class for the list of provided
arguments.

By just calling ``hubspot3`` you will get a list of all featured APIs that are available, e.g.:

.. code-block:: bash

    huspot3

    Usage:       hubspot3 -
                 hubspot3 - blog
                 hubspot3 - blog-comments
                 hubspot3 - broadcast
    [...]

By attaching the API name you can access the specific API endpoints:

.. code-block:: bash

    hubspot3 deals

    Usage:       hubspot3 deals
                 hubspot3 deals associate
                 hubspot3 deals create
                 hubspot3 deals get
    [...]

Each API method has it's own documentation and the help can be displayed like this:

.. code-block:: bash

    hubspot3 deals get -- --help

    [...]
    Docstring:   Supported ARGS/KWARGS are:
    DEAL_ID [--OPTIONS ...]
    --deal-id DEAL_ID [--OPTIONS ...]
    [...]

This will display the methods parameter list and how to pass them to the specific API endpoint, in this case you can
get the deal information for a specific deal with:

.. code-block:: bash

    hubspot3 --api-key xxxxxxxxx-xxxx-xxx-xxxx-xxxxx deals get --deal-id 100

.. note::

    You will notice the leading ``--`` in front of the ``--help`` parameter. Hubspot3 uses the ``python-fire`` library
    to generate a dynamic commandline interface for all API clients. If you don't add the ``--`` the help command will
    be passed to fire instead of the API method, so we have to set it.

Configuration file
^^^^^^^^^^^^^^^^^^

Instead of providing the API key (``--api-key``) or other settings (like ``--client-id`` or ``--timeout``) as
parameters you can also create a local JSON file, that contains all the settings you want to pass to the client:

.. code-block:: json

    {
        "api_key": "xxxxxxxxx-xxxx-xxx-xxxx-xxxxx",
        "timeout": 60
    }

Simply call the hubspot client with the ``--config`` parameter:

.. code-block:: bash

    hubspot3 --config config.json

Using ``stdin`` for parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Some of the data you want to pass to the hubspot3 may be sensitive or just too much to pass it as a regular
parameter. Therefore you can simply pass data from ``stdin`` to the client so that the data can be streamed and won't
occur in your shell history. To do so just use the token ``__stdin__`` for one of your parameters:

.. code-block:: bash

    hubspot3 --config config.json \
       contacts update --contact_id 451 \
       --data "__stdin__" < contact_data.json

In this case ``contact_data.json`` is a JSON file that contains the contacts data to update:

.. code-block:: json

    {
        "firstname": "Firstname",
        "lastname": "Lastname"
    }

Extending the APIs
------------------

There is one specialty in the way python-fire discovers the API clients: it will parse all classes that are derived
from ``BaseClient`` and are provided as a property within the ``hubspot3.Hubspot3`` class. Within these API clients
python-fire will look for public methods and provide them as a commandline API endpoint.

If you want to suppress python-fire to discover certain public methods (e.g. because the method will instantly make a
call to Hubspot or the method doesn't reflect an API endpoint) you can hide that method by extending
the ``__main__.Hubspot3CLIWrapper.IGNORED_ATTRS`` tuple within ``hubspot3.__main__.py``:

.. code-block:: python

    class Hubspot3CLIWrapper(object):

        IGNORED_ATTRS = ('me', 'usage_limits', 'my_method_to_hide')
