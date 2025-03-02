# update_assignee_steps.py
import os
import json
import requests
from behave import given, when, then

API_BASE = os.getenv("API_BASE", "http://backend:8000")

@given('an incident with id "17" exists with status "open"')
def step_impl_incident_17_exists(context):
    pass

@given('an incident with id "18" exists with status other than "open"')
def step_impl_incident_18_nonopen(context):
    pass

@when('a PATCH request is sent to "/incidents/17/update_assignee" with the payload')
def step_impl_update_assignee(context):
    url = f"{API_BASE}/incidents/17/update_assignee"
    payload = json.loads(context.text) if context.text else {}
    context.response = requests.patch(url, json=payload)

@when('a PATCH request is sent to "/incidents/18/update_assignee" with the payload')
def step_impl_update_assignee_nonopen(context):
    url = f"{API_BASE}/incidents/18/update_assignee"
    payload = json.loads(context.text) if context.text else {}
    context.response = requests.patch(url, json=payload)

@then('the incident assignee in the response should be "Ted"')
def step_impl_check_assignee(context):
    data = context.response.json()
    assert data.get("assignee") == "Ted"

@then('the response body should contain "Invalid assignee value"')
def step_impl_check_invalid_assignee(context):
    assert "Invalid assignee value" in context.response.text

@then('the response body should contain "Assignee can only be updated on open incidents"')
def step_impl_check_assignee_nonopen(context):
    assert "Assignee can only be updated on open incidents" in context.response.text
