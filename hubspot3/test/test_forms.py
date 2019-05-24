"""
testing hubspot3.deals
"""
import pytest
from hubspot3.forms import FormsClient, FormSubmissionClient
from hubspot3.error import HubspotNotFound
from hubspot3.test.globals import TEST_KEY


FORMS = FormsClient(api_key=TEST_KEY)
FORM_SUBMISSION = FormSubmissionClient(api_key=TEST_KEY)


# since we need to have an id to submit and to attempt to get a form,
# we need to be hacky here and fetch one upon loading this file.
BASE_FORM = FORMS.get_all(limit=1)[0]


def test_get_form():
    """
    attempts to get a form by id
    :see: https://developers.hubspot.com/docs/methods/forms/v2/get_form
    """
    with pytest.raises(HubspotNotFound):
        FORMS.get("not_a_form_id")

    form = FORMS.get(BASE_FORM["guid"])
    assert form
    assert isinstance(form, dict)


def test_get_all_forms():
    """
    attempts to get all forms
    :see: https://developers.hubspot.com/docs/methods/forms/v2/get_forms
    """
    all_forms = FORMS.get_all()
    assert all_forms
    assert isinstance(all_forms, list)
    assert len(all_forms) > 2

    limited_forms = FORMS.get_all(limit=2)
    assert isinstance(limited_forms, list)
    assert len(limited_forms) == 2

    offset_forms = FORMS.get_all(limit=1, offset=1)
    assert isinstance(offset_forms, list)
    assert len(offset_forms) == 1

    assert limited_forms[1] == offset_forms[0]


def test_submit_form():
    """
    tests submitting forms
    :see: https://developers.hubspot.com/docs/methods/forms/submit_form
    """
    context = {
        "hutk": "60c2ccdfe4892f0fa0593940b12c11aa",
        "ipAddress": "192.168.1.12",
        "pageUrl": "http://demo.hubapi.com/contact/",
        "pageName": "Contact Us",
    }
    bad_portal = "428357"
    data = {"email": "test123@gmail.com"}

    with pytest.raises(HubspotNotFound):
        FORM_SUBMISSION.submit_form(bad_portal, BASE_FORM["guid"], data, context=context)

    response = FORM_SUBMISSION.submit_form(
        BASE_FORM["portalId"], BASE_FORM["guid"], data, context=context
    )
    assert response
    assert response.status == FormSubmissionClient.ResponseCode.SUCCESS
