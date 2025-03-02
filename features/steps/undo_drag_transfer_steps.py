# undo_drag_transfer_steps.py
import os
import json
import requests
from behave import given, when, then

API_BASE = os.getenv("API_BASE", "http://backend:8000")

@given('incidents with ids "5" (source) and "6" (target) exist and a transfer has been performed')
def step_impl_incidents_transfer(context):
    pass  # Assume the transfer exists

@given('main alerts with ids [501, 502] were transferred from incident "5" to incident "6"')
def step_impl_main_alerts_transferred(context):
    pass  # Assume these alerts were transferred

@when('a POST request is sent to "/incidents/6/undo_drag_transfer/5" with the payload')
def step_impl_undo_drag_transfer(context):
    url = f"{API_BASE}/incidents/6/undo_drag_transfer/5"
    payload = json.loads(context.text) if context.text else {}
    context.response = requests.post(url, json=payload)

# @then('the response body should include "Undo drag transfer completed"')
# def step_impl_check_undo_drag_transfer(context):
#     assert "Undo drag transfer completed" in context.response.text
