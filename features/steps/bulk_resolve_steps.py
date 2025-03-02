# bulk_resolve_steps.py
import os
import json
import requests
from behave import given, when, then

API_BASE = os.getenv("API_BASE", "http://backend:8000")

@given('main alerts with ids "201" and "202" exist')
def step_impl_main_alerts_exist(context):
    # Assume alerts exist.
    pass

@when('a PATCH request is sent to "/main_alerts/bulk_resolve" with the payload')
def step_impl_bulk_resolve(context):
    url = f"{API_BASE}/main_alerts/bulk_resolve"
    payload = json.loads(context.text) if context.text else {}
    context.response = requests.patch(url, json=payload)

# @then('the response body should contain "Main alerts resolved"')
# def step_impl_check_bulk_resolve(context):
#     assert "Main alerts resolved" in context.response.text
