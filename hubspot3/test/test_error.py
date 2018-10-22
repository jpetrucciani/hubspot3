from hubspot3.error import HubspotError
from nose.tools import ok_


class MockResult(object):
    """
    Null Object pattern to prevent Null reference errors
    when there is no result
    """

    def __init__(self):
        self.status = 0
        self.body = ""
        self.msg = ""
        self.reason = ""


def test_unicode_error():
    result = MockResult()
    result.body = "A HapiException with unicode \\u8131 \xe2\x80\xa2\t"
    result.reason = "Why must everything have a reason?"
    request = {}
    for key in ("method", "host", "url", "timeout", "data", "headers"):
        request[key] = ""
    request["url"] = "http://adomain/with-unicode-\u8131"
    # Note the following line is missing the 'u' modifier on the string,
    # this is intentional to simulate poorly formatted input that should
    # still be handled without an exception
    request["data"] = "A HapiException with unicode \\u8131 \xe2\x80\xa2"
    request["headers"] = {"Cookie": "with unicode \\u8131 \xe2\x80\xa2"}

    exc = HubspotError(result, request)
    ok_(request["url"] in exc)
    ok_(result.reason in exc)


def test_error_with_no_result_or_request():
    exc = HubspotError(None, None, "a silly error")
    ok_("a silly error" in exc)


def test_error_string_summary():
    result = MockResult()
    result.body = {
        "status": "error",
        "message": "Property values were not valid"
    }

    # Make sure string representation of the error starts with the error
    # message returned by HubSpot.
    exc = HubspotError(result=result, request={})
    exc_str_first_line = str(exc).split("\n", 1)[1]
    ok_(exc_str_first_line.startswith(result.body["message"]))

    # Test falling back to a default error in case response doesn't contain one.
    exc = HubspotError(result=MockResult(), request={})
    exc_str_first_line = str(exc).split("\n", 1)[1]
    ok_(exc_str_first_line.startswith("Hubspot Error"))
