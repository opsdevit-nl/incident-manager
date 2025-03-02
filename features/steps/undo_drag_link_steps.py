# undo_drag_link_steps.py
import os
import json
import requests
from behave import given, when, then

API_BASE = os.getenv("API_BASE", "http://backend:8000")

@given('an incident with id "1" exists and a main alert with id "102" is linked to it')
def step_impl_incident_1_linked(context):
    pass  # Assume the linkage exists

@when('a POST request is sent to "/incidents/1/undo_drag_link_main_alert/102" with the payload')
def step_impl_undo_drag_link(context):
    url = f"{API_BASE}/incidents/1/undo_drag_link_main_alert/102"
    payload = json.loads(context.text) if context.text else {}
    context.response = requests.post(url, json=payload)

# @then('the response body should contain "Undo drag of main alert completed"')
# def step_impl_check_undo_drag_link(context):
#     assert "Undo drag of main alert completed" in context.response.text

@when('a POST request is sent to "/incidents/999/undo_drag_link_main_alert/102" with the payload')
def step_impl_undo_drag_link_nonexistent(context):
    url = f"{API_BASE}/incidents/999/undo_drag_link_main_alert/102"
    payload = json.loads(context.text) if context.text else {}
    context.response = requests.post(url, json=payload)

@then('the response body should contain "Source incident not found"')
def step_impl_check_source_not_found(context):
    assert "Source incident not found" in context.response.text
