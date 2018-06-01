import os
import json


def get_options():
    filename = "test_credentials.json"
    path = os.path.join(os.path.dirname(__file__), filename)
    options = {}
    if os.path.exists(path):
        try:
            raw_text = open(path).read()
        except IOError:
            raise Exception(
                "Unable to open '{}' for integration tests.\n"
                "If this file exists, then you are indicating you want to over"
                "ride the standard 'demo' creds with your own.\n"
                "However, it is currently inaccessible so that is a problem.".format(
                    filename
                )
            )
        try:
            options = json.loads(raw_text)
        except ValueError:
            raise Exception(
                "'{}' doesn't appear to be valid json!\n"
                "If this file exists, then you are indicating you want to override "
                "the standard 'demo' creds with your own.\nHowever, if I can't unde"
                "rstand the json inside of it, then that is a problem.".format(filename)
            )

        if not options.get("api_key") and not options.get("hapikey"):
            raise Exception(
                "'{}' seems to have no 'api_key' or 'access_token' specified!\n"
                "If this file exists, then you are indicating you want to override"
                "the standard 'demo' creds with your own.\nHowever, I'll need at "
                "least an API key to work with, or it definitely won't work.".format(
                    filename
                )
            )
        options["api_key"] = options.get("api_key") or options.get("hapikey")

    return options
