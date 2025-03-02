# check_permission_steps.py
import os
import requests
from behave import when, then

API_BASE = os.getenv("API_BASE", "http://backend:8000")

@when('a GET request is sent to "/check_permission/?role=admin"')
def step_impl_permission_admin(context):
    url = f"{API_BASE}/check_permission/?role=admin"
    context.response = requests.get(url)

@when('a GET request is sent to "/check_permission/?role=guest"')
def step_impl_permission_guest(context):
    url = f"{API_BASE}/check_permission/?role=guest"
    context.response = requests.get(url)

@then('the response body should contain')
def step_impl_check_permission_body(context):
    expected = context.text.strip()
    assert expected in context.response.text, f"Expected {expected} in response."

# @then('the response body should contain "Permission denied"')
# def step_impl_check_permission_denied(context):
#     assert "Permission denied" in context.response.text
