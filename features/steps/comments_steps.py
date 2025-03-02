# comments_steps.py
import os
import json
import requests
from behave import given, when, then

API_BASE = os.getenv("API_BASE", "http://backend:8000")

@given('an incident with id "4" exists')
def step_impl_incident_4_exists(context):
    pass  # Assume incident 4 exists

@given('a comment with id "401" exists on incident "4"')
def step_impl_comment_401_exists(context):
    pass  # Assume comment 401 exists

@given('a comment with id "402" exists on incident "4"')
def step_impl_comment_402_exists(context):
    pass  # Assume comment 402 exists

@when('a POST request is sent to "/incidents/4/comments/" with the payload')
def step_impl_add_comment(context):
    url = f"{API_BASE}/incidents/4/comments/"
    payload = json.loads(context.text) if context.text else {}
    context.response = requests.post(url, json=payload)

@when('a PATCH request is sent to "/incidents/4/comments/401" with the payload')
def step_impl_update_comment(context):
    url = f"{API_BASE}/incidents/4/comments/401"
    payload = json.loads(context.text) if context.text else {}
    context.response = requests.patch(url, json=payload)

@when('a DELETE request is sent to "/incidents/4/comments/402"')
def step_impl_delete_comment(context):
    url = f"{API_BASE}/incidents/4/comments/402"
    context.response = requests.delete(url)

@when('a PATCH request is sent to "/incidents/4/comments/999" with the payload')
def step_impl_update_nonexistent_comment(context):
    url = f"{API_BASE}/incidents/4/comments/999"
    payload = json.loads(context.text) if context.text else {}
    context.response = requests.patch(url, json=payload)

@when('a DELETE request is sent to "/incidents/4/comments/999"')
def step_impl_delete_nonexistent_comment(context):
    url = f"{API_BASE}/incidents/4/comments/999"
    context.response = requests.delete(url)

@then('the response body should include the comment details with "user6" as the login name')
def step_impl_check_comment_added(context):
    assert "user6" in context.response.text

@then('the response body should reflect the updated comment text')
def step_impl_check_comment_updated(context):
    assert "Updated comment text" in context.response.text

# @then('the response body should contain "Comment deleted"')
# def step_impl_check_comment_deleted(context):
#     assert "Comment deleted" in context.response.text

# @then('the response body should contain "Comment not found"')
# def step_impl_check_comment_not_found(context):
#     assert "Comment not found" in context.response.text
