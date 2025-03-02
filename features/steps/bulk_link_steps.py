# bulk_link_steps.py
import os
import json
import requests
from behave import given, when, then

API_BASE = os.getenv("API_BASE", "http://backend:8000")

@given('an incident with id "3" exists and is not discarded')
def step_impl_incident_3_exists(context):
    # Assume incident 3 exists and is active.
    pass

@given('main alerts with ids "301" and "302" exist and are not yet linked to incident "3"')
def step_impl_main_alerts_exist(context):
    # Assume these alerts exist.
    pass

@given('an incident with id "3" exists and is discarded')
def step_impl_incident_3_discarded(context):
    # Assume incident 3 is discarded.
    pass

@when('a POST request is sent to "/incidents/3/bulk_link_main_alerts" with the payload')
def step_impl_bulk_link(context):
    url = f"{API_BASE}/incidents/3/bulk_link_main_alerts"
    payload = json.loads(context.text) if context.text else {}
    context.response = requests.post(url, json=payload)

@when('a POST request is sent to "/incidents/999/bulk_link_main_alerts" with the payload')
def step_impl_bulk_link_nonexistent(context):
    url = f"{API_BASE}/incidents/999/bulk_link_main_alerts"
    payload = json.loads(context.text) if context.text else {}
    context.response = requests.post(url, json=payload)

@then('the response body should include "Bulk linking completed"')
def step_impl_check_bulk_success(context):
    assert "Bulk linking completed" in context.response.text

# @then('the response body should contain "Target incident not found"')
# def step_impl_check_target_not_found(context):
#     assert "Target incident not found" in context.response.text

# @then('the response body should contain "Cannot link main alerts to a discarded incident."')
# def step_impl_check_discarded(context):
#     assert "Cannot link main alerts to a discarded incident." in context.response.text
