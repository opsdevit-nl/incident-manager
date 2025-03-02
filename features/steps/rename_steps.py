# rename_steps.py
import os
import json
import requests
from behave import given, when, then

API_BASE = os.getenv("API_BASE", "http://backend:8000")

@given('an incident with id "12" exists')
def step_impl_incident_12_exists(context):
    pass

@when('a PATCH request is sent to "/incidents/12/rename" with the payload')
def step_impl_rename_incident(context):
    url = f"{API_BASE}/incidents/12/rename"
    payload = json.loads(context.text) if context.text else {}
    context.response = requests.patch(url, json=payload)

@then('the incident name in the response should be "New Incident Title"')
def step_impl_check_rename(context):
    data = context.response.json()
    assert data.get("incident_name") == "New Incident Title"

@when('a PATCH request is sent to "/incidents/999/rename" with the payload')
def step_impl_rename_nonexistent(context):
    url = f"{API_BASE}/incidents/999/rename"
    payload = json.loads(context.text) if context.text else {}
    context.response = requests.patch(url, json=payload)

# @then('the response body should contain "Incident not found"')
# def step_impl_check_incident_not_found(context):
#     assert "Incident not found" in context.response.text
