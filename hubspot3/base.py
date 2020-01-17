"""
base hubspot client class
"""
import http.client
import json
import logging
import time
import traceback
import urllib.request
import urllib.parse
import urllib.error
import zlib
from typing import Callable, List, Optional, Union
from typing_extensions import Literal
from hubspot3 import utils
from hubspot3.utils import force_utf8
from hubspot3.error import (
    HubspotBadConfig,
    HubspotBadRequest,
    HubspotConflict,
    HubspotError,
    HubspotNoConfig,
    HubspotNotFound,
    HubspotRateLimited,
    HubspotServerError,
    HubspotTimeout,
    HubspotUnauthorized,
)


class BaseClient:
    """Base abstract object for interacting with the HubSpot APIs"""

    # These rules are too restrictive for the `__init__()` method and attributes.
    # pylint: disable=too-many-arguments,too-many-instance-attributes

    # Controls how long we sleep for during retries, overridden by unittests
    # so tests run faster
    sleep_multiplier = 1

    def __init__(
        self,
        api_key: str = None,
        access_token: str = None,
        refresh_token: str = None,
        client_id: str = None,
        client_secret: str = None,
        oauth2_token_getter: Optional[
            Callable[[Literal["access_token", "refresh_token"], str], str]
        ] = None,
        oauth2_token_setter: Optional[
            Callable[[Literal["access_token", "refresh_token"], str, str], None]
        ] = None,
        timeout: int = 10,
        mixins: List = None,
        api_base: str = "api.hubapi.com",
        debug: bool = False,
        disable_auth: bool = False,
        **extra_options
    ) -> None:
        super(BaseClient, self).__init__()
        # reverse so that the first one in the list because the first parent
        if not mixins:
            mixins = []
        mixins.reverse()
        for mixin_class in mixins:
            if mixin_class not in self.__class__.__bases__:
                self.__class__.__bases__ = (mixin_class,) + self.__class__.__bases__

        self.api_key = api_key
        # These are used as fallbacks if there aren't setters/getters, or if no remote tokens can be
        # found. The properties without `__` prefixes should generally be used instead of these.
        self.__access_token = access_token
        self.__refresh_token = refresh_token
        self.client_id = client_id
        self.client_secret = client_secret
        if (oauth2_token_getter is None) != (oauth2_token_setter is None):
            raise HubspotBadConfig(
                "You must either specify both the oauth2 token setter and getter, or neither."
            )
        self.oauth2_token_getter = oauth2_token_getter
        self.oauth2_token_setter = oauth2_token_setter
        self.log = utils.get_log("hubspot3")
        if not disable_auth:
            if self.api_key and self.access_token:
                raise HubspotBadConfig("Cannot use both api_key and access_token.")
            if not (self.api_key or self.access_token or self.refresh_token):
                raise HubspotNoConfig("Missing required credentials.")
        self.options = {
            "api_base": api_base,
            "debug": debug,
            "disable_auth": disable_auth,
            "timeout": timeout,
        }
        self.options.update(extra_options)
        self._prepare_connection_type()

    @property
    def credentials(self):
        """
        Credentials to be used when a client needs to instantiate another one.
        Example:
        association_client = AssociationsClient(**self.credentials)
        """
        return {
            "api_key": self.api_key,
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "oauth2_token_getter": self.oauth2_token_getter,
            "oauth2_token_setter": self.oauth2_token_setter,
        }

    @property
    def access_token(self):
        if self.oauth2_token_getter:
            return (
                self.oauth2_token_getter("access_token", self.client_id)
                or self.__access_token
            )
        return self.__access_token

    @access_token.setter
    def access_token(self, access_token):
        if self.oauth2_token_setter:
            self.oauth2_token_setter("access_token", self.client_id, access_token)
        self.__access_token = access_token

    @property
    def refresh_token(self):
        if self.oauth2_token_getter:
            return (
                self.oauth2_token_getter("refresh_token", self.client_id)
                or self.__refresh_token
            )
        return self.__refresh_token

    @refresh_token.setter
    def refresh_token(self, refresh_token):
        if self.oauth2_token_setter:
            self.oauth2_token_setter("refresh_token", self.client_id, refresh_token)
        else:
            self.__refresh_token = refresh_token

    def _prepare_connection_type(self):
        connection_types = {
            "http": http.client.HTTPConnection,
            "https": http.client.HTTPSConnection,
        }
        parts = self.options["api_base"].split("://")
        protocol = (parts[0:-1] + ["https"])[0]
        self.options["connection_type"] = connection_types[protocol]
        self.options["protocol"] = protocol
        self.options["api_base"] = parts[-1]

    def _get_path(self, subpath):
        """get the full api url for the given subpath on this client"""
        return subpath

    def _prepare_request_auth(self, subpath, params, data, opts):
        if self.api_key:
            params["hapikey"] = params.get("hapikey") or self.api_key

    def _prepare_request(
        self,
        subpath,
        params,
        data,
        opts,
        doseq=False,
        query="",
        retried=False,
        properties=None,
    ):
        params = params or {}
        properties = properties or []
        self._prepare_request_auth(subpath, params, data, opts)

        if opts.get("hub_id") or opts.get("portal_id"):
            params["portalId"] = opts.get("hub_id") or opts.get("portal_id")
        if query is None:
            query = ""
        if query and query.startswith("?"):
            query = query[1:]
        if query and not query.startswith("&"):
            query = "&" + query
        url = opts.get("url") or "/{}?{}{}".format(
            self._get_path(subpath), urllib.parse.urlencode(params, doseq), query
        )
        headers = opts.get("headers") or {}
        headers.update(
            {
                "Accept-Encoding": "gzip",
                "Content-Type": opts.get("content_type") or "application/json",
            }
        )
        if self.access_token:
            headers.update({"Authorization": "Bearer {}".format(self.access_token)})

        if data and headers["Content-Type"] == "application/json" and not retried:
            data = json.dumps(data)

        for hs_property in properties:
            url += "&property={}".format(hs_property)

        return url, headers, data

    def _create_request(self, conn, method, url, headers, data):
        conn.request(method, url, data, headers)
        params = {
            "method": method,
            "url": url,
            "data": data,
            "headers": headers,
            "host": conn.host,
            "timeout": conn.timeout,
        }
        return params

    def _gunzip_body(self, body):
        return zlib.decompress(body)

    def _process_body(self, data, gzipped):
        if gzipped:
            return force_utf8(self._gunzip_body(data))
        return data

    def _execute_request_raw(self, conn, request):
        try:
            result = conn.getresponse()
        except Exception:
            raise HubspotTimeout(None, request, traceback.format_exc())

        encoding = [i[1] for i in result.getheaders() if i[0] == "content-encoding"]
        possibly_encoded = result.read()
        try:
            possibly_encoded = zlib.decompress(possibly_encoded, 16 + zlib.MAX_WBITS)
        except Exception:
            pass
        result.body = self._process_body(
            possibly_encoded, len(encoding) and encoding[0] == "gzip"
        )

        conn.close()
        if result.status in (404, 410):
            raise HubspotNotFound(result, request)
        if result.status == 401:
            raise HubspotUnauthorized(result, request)
        if result.status == 409:
            raise HubspotConflict(result, request)
        if result.status == 429:
            raise HubspotRateLimited(result, request)
        if 400 <= result.status < 500 or result.status == 501:
            raise HubspotBadRequest(result, request)
        if result.status >= 500:
            raise HubspotServerError(result, request)

        return result

    def _execute_request(self, conn, request):
        result = self._execute_request_raw(conn, request)
        return result.body

    def _digest_result(self, data):
        if data:
            if isinstance(data, bytes):
                data = utils.force_utf8(data)
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except ValueError:
                    pass

        return data

    def _prepare_request_retry(self, method, url, headers, data):
        pass

    def _call_raw(
        self,
        subpath,
        params=None,
        method="GET",
        data=None,
        doseq=False,
        query="",
        retried=False,
        properties=None,
        **options
    ):
        opts = self.options.copy()
        opts.update(options)

        debug = opts.get("debug")

        url, headers, data = self._prepare_request(
            subpath,
            params,
            data,
            opts,
            doseq=doseq,
            query=query,
            retried=retried,
            properties=properties,
        )

        if debug:
            print(
                json.dumps(
                    {"url": url, "headers": headers, "data": data},
                    sort_keys=True,
                    indent=2,
                )
            )

        kwargs = {"timeout": opts["timeout"]}

        num_retries = opts.get("number_retries", 2)

        # Never retry a POST, PUT, or DELETE unless explicitly told to
        if method != "GET" and not opts.get("retry_on_post"):
            num_retries = 0
        if num_retries > 6:
            num_retries = 6

        emergency_brake = 10
        try_count = 0
        while True:
            emergency_brake -= 1
            # avoid getting burned by any mistakes in While loop logic
            if emergency_brake < 1:
                break
            try:
                try_count += 1
                connection = opts["connection_type"](opts["api_base"], **kwargs)
                request_info = self._create_request(
                    connection, method, url, headers, data
                )
                result = self._execute_request_raw(connection, request_info)
                break
            except HubspotUnauthorized:
                self.log.warning("401 Unauthorized response to API request.")
                if (
                    self.access_token
                    and self.refresh_token
                    and self.client_id
                    and self.client_secret
                ):
                    if retried:
                        self.log.error(
                            "Refreshed token, but request still was not authorized. "
                            "You may need to grant additional permissions."
                        )
                        raise

                    from hubspot3.oauth2 import OAuth2Client

                    self.log.info("Refreshing access token")
                    try:
                        client = OAuth2Client(**self.options)
                        refresh_result = client.refresh_tokens(
                            client_id=self.client_id,
                            client_secret=self.client_secret,
                            refresh_token=self.refresh_token,
                        )
                        self.access_token = refresh_result["access_token"]
                        self.refresh_token = refresh_result["refresh_token"]
                        self.log.info(
                            "Retrying with new token {}".format(self.access_token)
                        )
                    except Exception as exception:
                        self.log.error(
                            "Unable to refresh access_token: {}".format(exception)
                        )
                        raise
                    return self._call_raw(
                        subpath,
                        params=params,
                        method=method,
                        data=data,
                        doseq=doseq,
                        query=query,
                        retried=True,
                        **options
                    )
                if self.access_token:
                    self.log.warning(
                        "In order to enable automated refreshing of your access token, please "
                        "provide a client ID, client secret and refresh token in addition to the "
                        "access token."
                    )
                raise
            except HubspotError as exception:
                if try_count > num_retries:
                    logging.warning("Too many retries for {}".format(url))
                    raise
                # Don't retry errors from 300 to 499
                if exception.result and 300 <= exception.result.status < 500:
                    raise
                self._prepare_request_retry(method, url, headers, data)
                self.log.warning(
                    "HubspotError {} calling {}, retrying".format(exception, url)
                )
            # exponential back off
            # wait 0 seconds, 1 second, 3 seconds, 7 seconds, 15 seconds, etc
            time.sleep((pow(2, try_count - 1) - 1) * self.sleep_multiplier)
        return result

    def _call(
        self,
        subpath: str,
        params: dict = None,
        method: str = "GET",
        data: Union[str, dict, list] = None,
        doseq: bool = False,
        query: str = "",
        raw: bool = False,
        properties: list = None,
        **options
    ):
        result = self._call_raw(
            subpath,
            params=params,
            method=method,
            data=data,
            doseq=doseq,
            query=query,
            retried=False,
            properties=properties,
            **options
        )
        return result if raw else self._digest_result(result.body)
