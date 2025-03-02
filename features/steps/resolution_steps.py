# resolution_steps.py
import os
import json
import requests
from behave import given, when, then

API_BASE = os.getenv("API_BASE", "http://backend:8000")

@given('an incident with id "8" exists')
def step_impl_incident_8_exists(context):
    pass

@when('a PATCH request is sent to "/incidents/8/resolve" with the payload')
def step_impl_resolve_incident(context):
    url = f"{API_BASE}/incidents/8/resolve"
    payload = json.loads(context.text) if context.text else {}
    context.response = requests.patch(url, json=payload)

@then('the incident status in the response should be "resolved"')
def step_impl_check_resolved(context):
    data = context.response.json()
    assert data.get("status") == "resolved"

@given('an incident with id "9" exists')
def step_impl_incident_9_exists(context):
    pass

@when('a PATCH request is sent to "/incidents/9/definitively_resolve" with the payload')
def step_impl_definitively_resolve(context):
    url = f"{API_BASE}/incidents/9/definitively_resolve"
    payload = json.loads(context.text) if context.text else {}
    context.response = requests.patch(url, json=payload)

@then('the incident status in the response should be "def-resolved"')
def step_impl_check_def_resolved(context):
    data = context.response.json()
    assert data.get("status") == "def-resolved"

@then('the "definitively_resolved" flag should be true')
def step_impl_check_flag(context):
    data = context.response.json()
    assert data.get("definitively_resolved") is True

@when('a PATCH request is sent to "/incidents/999/resolve" with the payload')
def step_impl_resolve_nonexistent(context):
    url = f"{API_BASE}/incidents/999/resolve"
    payload = json.loads(context.text) if context.text else {}
    context.response = requests.patch(url, json=payload)

# @then('the response body should contain "Incident not found"')
# def step_impl_check_incident_not_found(context):
#     assert "Incident not found" in context.response.text

@given('an incident with id "10" exists with status "resolved"')
def step_impl_incident_10_resolved(context):
    pass

@when('a PATCH request is sent to "/incidents/10/reopen" with the payload')
def step_impl_reopen_incident(context):
    url = f"{API_BASE}/incidents/10/reopen"
    payload = json.loads(context.text) if context.text else {}
    context.response = requests.patch(url, json=payload)

@then('the incident status in the response should be "open"')
def step_impl_check_reopen(context):
    data = context.response.json()
    assert data.get("status") == "open"

@given('an incident with id "11" exists and is definitively resolved')
def step_impl_incident_11_def_resolved(context):
    pass

@when('a PATCH request is sent to "/incidents/11/reopen" with the payload')
def step_impl_reopen_def_resolved(context):
    url = f"{API_BASE}/incidents/11/reopen"
    payload = json.loads(context.text) if context.text else {}
    context.response = requests.patch(url, json=payload)

@then('the response body should contain "Incident is definitively resolved and cannot be reopened"')
def step_impl_check_reopen_fail(context):
    assert "Incident is definitively resolved and cannot be reopened" in context.response.text
