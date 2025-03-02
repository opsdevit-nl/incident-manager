# drag_link_steps.py
import os
import json
import requests
from behave import given, when, then

API_BASE = os.getenv("API_BASE", "http://backend:8000")



@given('a main alert with id "102" exists and is not already linked to incident "1"')
def step_impl_main_alert_102_exists(context):
    pass  # Assume alert 102 exists and is unlinked

@given('a main alert with id "102" is linked to an incident that is definitively resolved')
def step_impl_main_alert_102_resolved(context):
    pass  # Assume alert 102 is linked to a def-resolved incident

@when('a POST request is sent to "/incidents/1/drag_link_main_alert/102" with the payload')
def step_impl_drag_link(context):
    url = f"{API_BASE}/incidents/1/drag_link_main_alert/102"
    payload = json.loads(context.text) if context.text else {}
    context.response = requests.post(url, json=payload)

@when('a POST request is sent to "/incidents/999/drag_link_main_alert/102" with the payload')
def step_impl_drag_link_nonexistent(context):
    url = f"{API_BASE}/incidents/999/drag_link_main_alert/102"
    payload = json.loads(context.text) if context.text else {}
    context.response = requests.post(url, json=payload)

@then('the response body should indicate the main alert has been transferred')
def step_impl_check_drag_link(context):
    assert "transferred" in context.response.text

# @then('the response body should contain "Target incident not found"')
# def step_impl_check_target_not_found(context):
#     assert "Target incident not found" in context.response.text

@then('the response body should contain "Cannot move main alert from a definitively resolved incident"')
def step_impl_check_def_resolved(context):
    assert "Cannot move main alert from a definitively resolved incident" in context.response.text
