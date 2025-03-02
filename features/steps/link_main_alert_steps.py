# link_main_alert_steps.py
import os
import json
import requests
from behave import given, when, then

API_BASE = os.getenv("API_BASE", "http://backend:8000")

# @given('an incident with id "1" exists and is not discarded')
# def step_impl_incident_1_exists(context):
#     pass

@given('a main alert with id "101" exists')
def step_impl_main_alert_101_exists(context):
    pass

@given('an incident with id "2" exists and its status is "discarded"')
def step_impl_incident_2_discarded(context):
    pass

@given('an incident with id "1" exists and already has main alert id "101" linked')
def step_impl_incident_1_already_linked(context):
    pass

@when('a POST request is sent to "/incidents/1/link_main_alert" with the payload')
def step_impl_link_main_alert(context):
    url = f"{API_BASE}/incidents/1/link_main_alert"
    payload = json.loads(context.text) if context.text else {}
    context.response = requests.post(url, json=payload)

@when('a POST request is sent to "/incidents/999/link_main_alert" with the payload')
def step_impl_link_main_alert_nonexistent(context):
    url = f"{API_BASE}/incidents/999/link_main_alert"
    payload = json.loads(context.text) if context.text else {}
    context.response = requests.post(url, json=payload)

@when('a POST request is sent to "/incidents/2/link_main_alert" with the payload')
def step_impl_link_main_alert_discarded(context):
    url = f"{API_BASE}/incidents/2/link_main_alert"
    payload = json.loads(context.text) if context.text else {}
    context.response = requests.post(url, json=payload)

@then('the response body should include "Main alert linked to target incident"')
def step_impl_check_link_success(context):
    assert "Main alert linked to target incident" in context.response.text

# @then('the response body should contain "Target incident not found"')
# def step_impl_check_link_target_not_found(context):
#     assert "Target incident not found" in context.response.text

@then('the response body should contain "Cannot link a main alert to a discarded incident"')
def step_impl_check_link_discarded(context):
    assert "Cannot link a main alert to a discarded incident" in context.response.text

# @then('the response body should contain "Main alert already linked to this incident"')
# def step_impl_check_link_already(context):
#     assert "Main alert already linked to this incident" in context.response.text
