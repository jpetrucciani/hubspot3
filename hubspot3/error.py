"""
hubspot3 error helpers
"""
import json

from hubspot3.utils import force_utf8, uglify_hapikey


class EmptyResult:
    """
    Null Object pattern to prevent Null reference errors
    when there is no result
    """

    def __init__(self):
        self.status = 0
        self.body = ""
        self.msg = ""
        self.reason = ""


class HubspotError(ValueError):
    """Any problems get thrown as HubspotError exceptions with the relevant info inside"""

    as_str_template = """
{error_message}

---- request ----
{method} {host}{url}, [timeout={timeout}]

---- body ----
{body}

---- headers ----
{headers}

---- result ----
{result_status}

---- body -----
{result_body}

---- headers -----
{result_headers}

---- reason ----
{result_reason}

---- trigger error ----
{error}
        """

    def __contains__(self, item):
        """tests if the given item text is in the error text"""
        return item in self.__str__()

    def __init__(self, result, request, err=None):
        super(HubspotError, self).__init__(result and result.reason or "Unknown Reason")
        if result is None:
            self.result = EmptyResult()
        else:
            self.result = result
        if request is None:
            request = {}
        if "url" in request:
            request["url"] = uglify_hapikey(request["url"])
        self.request = request
        self.err = err

    def __str__(self):
        params = {}
        request_keys = ("method", "host", "url", "data", "headers", "timeout", "body")
        result_attrs = ("status", "reason", "msg", "body", "headers")
        params["error"] = self.err
        params["error_message"] = "Hubspot Error"
        if self.result.body:
            try:
                result_body = json.loads(force_utf8(self.result.body))
            except ValueError:
                result_body = {}
            params["error_message"] = result_body.get("message", "Hubspot Error")
        for key in request_keys:
            params[key] = self.request.get(key)
        for attr in result_attrs:
            params["result_{}".format(attr)] = getattr(self.result, attr, "")

        params = self._dict_vals_to_str(params)
        return self.as_str_template.format(**params)

    def _dict_vals_to_str(self, data):
        unicode_data = {}
        for key, val in data.items():
            if not val:
                unicode_data[key] = ""
            if isinstance(val, bytes):
                unicode_data[key] = force_utf8(val)
            elif isinstance(val, str):
                unicode_data[key] = val
            else:
                unicode_data[key] = str(type(val))
        return unicode_data


class HubspotBadConfig(Exception):
    """misconfigured api_key and/or access_token credentials client"""


class HubspotNoConfig(Exception):
    """no api_key or access_token credentials were passed to the client"""


# Create more specific error cases, to make filtering errors easier
class HubspotBadRequest(HubspotError):
    """most 40X results and 501 results"""


class HubspotNotFound(HubspotError):
    """404 and 410 results"""


class HubspotTimeout(HubspotError):
    """socket timeouts, sslerror, and 504"""


class HubspotUnauthorized(HubspotError):
    """401 Unauthorized errors"""


class HubspotConflict(HubspotError):
    """409 conflict errors"""


class HubspotServerError(HubspotError):
    """most 500 errors"""


class HubspotRateLimited(HubspotError):
    """exception for when we're rate limited"""
