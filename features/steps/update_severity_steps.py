# update_severity_steps.py
import os
import json
import requests
from behave import given, when, then

API_BASE = os.getenv("API_BASE", "http://backend:8000")

@given('an incident with id "13" exists with status "open"')
def step_impl_incident_13_exists(context):
    pass

@given('an incident with id "14" exists with status other than "open"')
def step_impl_incident_14_nonopen(context):
    pass

@when('a PATCH request is sent to "/incidents/13/update_severity" with the payload')
def step_impl_update_severity(context):
    url = f"{API_BASE}/incidents/13/update_severity"
    payload = json.loads(context.text) if context.text else {}
    context.response = requests.patch(url, json=payload)

@when('a PATCH request is sent to "/incidents/14/update_severity" with the payload')
def step_impl_update_severity_nonopen(context):
    url = f"{API_BASE}/incidents/14/update_severity"
    payload = json.loads(context.text) if context.text else {}
    context.response = requests.patch(url, json=payload)

@then('the incident severity in the response should be "HIGH"')
def step_impl_check_severity(context):
    data = context.response.json()
    assert data.get("severity") == "HIGH"

@then('the response body should contain "Invalid severity value"')
def step_impl_check_invalid_severity(context):
    assert "Invalid severity value" in context.response.text

@then('the response body should contain "Severity can only be updated on open incidents"')
def step_impl_check_severity_nonopen(context):
    assert "Severity can only be updated on open incidents" in context.response.text
