"""
allow threaded execution of hubspot api calls
"""
import io
import pycurl


class Hubspot3ThreadedError(ValueError):
    """general exception for the multithreading mixin"""

    def __init__(self, curl):
        super(Hubspot3ThreadedError, self).__init__(curl.body.getvalue())
        self.curl_call = curl
        self.response_body = self.curl_call.body.getvalue()
        self.response_headers = self.curl_call.response_headers.getvalue()

    def __str__(self):
        return (
            "\n---- request ----\n{} {}{} [timeout={}]\n\n---- body ----\n{}\n\n---- headers"
            " ----\n{}\n\n---- result ----\n{}\n\n---- body ----\n{}\n\n---- headers "
            "----\n{}".format(
                getattr(self.curl_call, "method", ""),
                self.curl_call.host,
                self.curl_call.path,
                self.curl_call.timeout,
                self.curl_call.data,
                self.curl_call.headers,
                self.curl_call.status,
                self.response_body,
                self.response_headers,
            )
        )

    def __unicode__(self):
        return self.__str__()


class PyCurlMixin(object):
    """
    The the mixins in this file require PyCURL in order to make parallel API calls.
    On OSX and Linux machines, PyCURL can be installed via pip (run "pip install pycurl" ).
    For windows machines, pre-compiled PyCURL binaries can be downloaded
    [here for python 2.6 and 2.7](http://www.lfd.uci.edu/~gohlke/pythonlibs/#pycurl), and
    [here for python 2.5](http://www.lfd.uci.edu/~gohlke/pythonlibs/#pycurl).
    PyCurlMixin relies on PyCurl, which is a library around libcurl which enables efficient
    multi-threaded requests.  Use this mixin when you want to be able to execute multiple
    API calls at once, instead of in sequence.

    Enable by calling client.mixin(PyCurlMixin) after importing PyCurlMixin and instantiating
    the client of your choice.

    Once enabled, use like so:
        client.my_api_call()
        client.my_other_api_call()
        results = client.process_queue()

    The results object will then return a list of dicts, containing the response to your calls
    in the order they were called. Dicts have keys: data, code, and
    (if something went wrong) exception.
    """

    def _call(
        self, subpath, params=None, method="GET", data=None, doseq=False, **options
    ):
        opts = self.options.copy()
        opts.update(options)

        request_parts = self._prepare_request(subpath, params, data, opts, doseq=doseq)
        self._enqueue(request_parts)

    def _enqueue(self, parts):
        if not hasattr(self, "_queue"):
            self._queue = []

        self._queue.append(parts)

    def _create_curl(self, url, headers, data):
        curl_call = pycurl.Curl()

        full_url = "{}://{}{}".format(
            self.options["protocol"], self.options["api_base"], url
        )

        curl_call.timeout = self.options["timeout"]
        curl_call.protocol = self.options["protocol"]
        curl_call.host = self.options["api_base"]
        curl_call.path = url
        curl_call.full_url = full_url
        curl_call.headers = headers
        curl_call.data = data

        curl_call.status = -1
        curl_call.body = io.StringIO()
        curl_call.response_headers = io.StringIO()

        curl_call.setopt(curl_call.URL, curl_call.full_url)
        curl_call.setopt(curl_call.TIMEOUT, self.options["timeout"])
        curl_call.setopt(curl_call.WRITEFUNCTION, curl_call.body.write)
        curl_call.setopt(curl_call.HEADERFUNCTION, curl_call.response_headers.write)

        if headers:
            curl_call.setopt(
                curl_call.HTTPHEADER,
                ["{}: {}".format(x, y) for x, y in list(headers.items())],
            )

        if data:
            curl_call.data_out = io.StringIO(data)
            curl_call.setopt(curl_call.READFUNCTION, curl_call.data_out.getvalue)

        return curl_call

    def process_queue(self):
        """
        Processes all API calls since last invocation, returning a list of data
        in the order the API calls were created
        """
        multi_curl = pycurl.CurlMulti()
        multi_curl.handles = []

        # Loop the queue and create Curl objects for processing
        for item in self._queue:
            curl_call = self._create_curl(*item)
            multi_curl.add_handle(curl_call)
            multi_curl.handles.append(curl_call)

        # Process the collected Curl handles
        num_handles = len(multi_curl.handles)
        while num_handles:
            while 1:
                # Perform the calls
                ret, num_handles = multi_curl.perform()
                if ret != pycurl.E_CALL_MULTI_PERFORM:
                    break
            multi_curl.select(1.0)

        # Collect data
        results = []
        for curl_call in multi_curl.handles:
            curl_call.status = curl_call.getinfo(curl_call.HTTP_CODE)
            if "Content-Encoding: gzip" in curl_call.response_headers.getvalue():
                curl_call.body = io.StringIO(
                    self._gunzip_body(curl_call.body.getvalue())
                )
            result = {
                "data": self._digest_result(curl_call.body.getvalue()),
                "code": curl_call.status,
            }
            if not curl_call.status or curl_call.status >= 400:
                # Don't throw the exception because some might have succeeded
                result["exception"] = Hubspot3ThreadedError(curl_call)

            results.append(result)

        # cleanup
        for curl_call in multi_curl.handles:
            if hasattr(curl_call, "data_out"):
                curl_call.data_out.close()

            curl_call.body.close()
            curl_call.response_headers.close()
            curl_call.close()
            multi_curl.remove_handle(curl_call)

        multi_curl.close()
        del multi_curl.handles
        self._queue = []

        return results
