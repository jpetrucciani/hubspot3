"""
hubspot forms api
"""
import json
from urllib.parse import urlencode
from http.client import HTTPResponse
from hubspot3.base import BaseClient
from hubspot3.error import HubspotNotFound, HubspotServerError
from typing import Dict


FORMS_API_VERSION = 2


class FormSubmissionClient(BaseClient):
    """allows acccess to submit forms via the hubspot api"""

    class ResponseCode:
        """form submission response codes enum"""

        SUCCESS = 204
        SUCCESS_AND_REDIRECT = 302
        NOT_FOUND = 404
        ERROR = 500

    def __init__(self, *args, **kwargs) -> None:
        """form submission client constructor"""
        kwargs.update({"disable_auth": True})
        super(FormSubmissionClient, self).__init__(*args, **kwargs)
        self.options["api_base"] = "forms.hubspot.com"

    def _get_path(self, subpath: str) -> str:
        """api path for submitting to a form"""
        return f"/uploads/form/v{FORMS_API_VERSION}/{subpath}"

    def submit_form(
        self,
        portal_id: str,
        form_guid: str,
        data: dict,
        context: dict = None,
        **options
    ) -> HTTPResponse:
        """
        submit to a form on hubspot
        does not require credentials

        this will urlencode the data automatically
        and if you pass a context:
            it will json dump for you, and place inside the data

        :see: https://developers.hubspot.com/docs/methods/forms/submit_form
        """
        if context:
            data["hs_context"] = json.dumps(context)
        subpath = f"{portal_id}/{form_guid}"
        opts = {"content_type": "application/x-www-form-urlencoded"}
        options.update(opts)
        response = self._call(
            subpath, method="POST", data=urlencode(data), raw=True, **options
        )
        if response.status in [
            FormSubmissionClient.ResponseCode.SUCCESS,
            FormSubmissionClient.ResponseCode.SUCCESS_AND_REDIRECT,
        ]:
            return response
        if response.status == FormSubmissionClient.ResponseCode.NOT_FOUND:
            raise HubspotNotFound(response, None)
        if response.status == FormSubmissionClient.ResponseCode.ERROR:
            raise HubspotServerError(response, None)

        # shouldn't ever get here, but raise anyways
        raise HubspotServerError(response, None)


class FormsClient(BaseClient):
    """allows access to form data inside your hubspot account"""

    def __init__(self, *args, **kwargs) -> None:
        """forms client constructor"""
        super(FormsClient, self).__init__(*args, **kwargs)

    def _get_path(self, subpath) -> str:
        """api path for the forms related calls"""
        return f"forms/v{FORMS_API_VERSION}/{subpath}"

    def get(self, form_id: str, **options) -> Dict:
        """
        get a form by its form_id
        :see: https://developers.hubspot.com/docs/methods/forms/v2/get_form
        """
        return self._call(f"forms/{form_id}", method="GET", **options)

    def get_all(self, limit: int = -1, offset: int = 0, **options) -> list:
        """
        get all forms from this hubspot portal.
        :see: https://developers.hubspot.com/docs/methods/forms/v2/get_forms
        """
        params = {"offset": offset}
        if limit > 0:
            params["limit"] = limit
        return self._call("forms", method="GET", params=params)
