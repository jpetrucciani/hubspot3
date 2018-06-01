"""
hubspot forms api
"""
from hubspot3.base import BaseClient


class FormSubmissionClient(BaseClient):
    """allows acccess to the forms api"""

    def __init__(self, *args, **kwargs):
        super(FormSubmissionClient, self).__init__(*args, **kwargs)
        self.options["api_base"] = "forms.hubspot.com"

    def _get_path(self, subpath):
        return "/uploads/form/v2/{}".format(subpath)

    def submit_form(self, portal_id, form_guid, data, **options):
        subpath = "{}/{}".format(portal_id, form_guid)
        opts = {"content_type": "application/x-www-form-urlencoded"}
        options.update(opts)
        return self._call(
            subpath=None,
            url=self._get_path(subpath),
            method="POST",
            data=data,
            **options
        )
