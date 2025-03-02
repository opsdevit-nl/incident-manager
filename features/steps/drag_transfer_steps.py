# drag_transfer_steps.py
import os
import json
import requests
from behave import given, when, then

API_BASE = os.getenv("API_BASE", "http://backend:8000")

@given('two incidents exist with ids "5" (source) and "6" (target) where the target is not discarded')
def step_impl_incidents_exist(context):
    pass  # Assume incidents exist

@when('a POST request is sent to "/incidents/6/drag_transfer/5" with the payload')
def step_impl_drag_transfer(context):
    url = f"{API_BASE}/incidents/6/drag_transfer/5"
    payload = json.loads(context.text) if context.text else {}
    context.response = requests.post(url, json=payload)

@when('a POST request is sent to "/incidents/6/drag_transfer/999" with the payload')
def step_impl_drag_transfer_nonexistent(context):
    url = f"{API_BASE}/incidents/6/drag_transfer/999"
    payload = json.loads(context.text) if context.text else {}
    context.response = requests.post(url, json=payload)

@then('the response body should include "Incident transferred via drag & drop"')
def step_impl_check_drag_transfer(context):
    assert "Incident transferred via drag & drop" in context.response.text

# @then('the response body should contain "Incident not found"')
# def step_impl_check_incident_not_found(context):
#     assert "Incident not found" in context.response.text

@when('a POST request is sent to "/incidents/7/drag_transfer/5" with the payload')
def step_impl_drag_transfer_discarded(context):
    url = f"{API_BASE}/incidents/7/drag_transfer/5"
    payload = json.loads(context.text) if context.text else {}
    context.response = requests.post(url, json=payload)

@then('the response body should contain "Cannot transfer into a discarded incident"')
def step_impl_check_transfer_discarded(context):
    assert "Cannot transfer into a discarded incident" in context.response.text
