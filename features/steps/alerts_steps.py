# features/steps/alerts_steps.py
import json
import requests
from behave import given, when, then

API_BASE = "http://backend:8000"  # Update if your API base URL is different

@given('a valid bulk alerts payload')
def step_impl(context):
    # Set up a valid bulk alerts payload
    context.payload = {
        "alerts": [
            {
                "status": "new",
                "labels": { "alertname": "CPU_Alert", "destination": "pls", "host": "server1" },
                "annotations": { "description": "High CPU usage" }
            }
        ],
        "externalURL": "http://example.com",
        "last_modified_by": "user1"
    }

@given('an invalid JSON payload')
def step_impl(context):
    # You might simulate invalid JSON by assigning a string that isn't valid JSON.
    # Later, you'll pass this raw string directly to the HTTP call.
    context.raw_payload = "this is not valid JSON"

@given('a legacy alert payload')
def step_impl(context):
    context.payload = {
        "message": "Legacy alert message",
        "source": "tab",
        "host": "server2",
        "state": "1",
        "wikilink": "Undefined",
        "status": "new"
    }

@when('a POST request is sent to "/alerts/" with the payload')
def step_impl(context):
    url = f"{API_BASE}/alerts/"
    # Decide based on context if you're sending valid JSON or simulating an invalid JSON case.
    try:
        payload = context.payload
    except AttributeError:
        payload = context.raw_payload
    context.response = requests.post(url, json=payload)

@when('a POST request is sent to "/alerts/"')
def step_impl(context):
    url = f"{API_BASE}/alerts/"
    context.response = requests.post(url)

@then('the response status should be {status_code:d}')
def step_impl(context, status_code):
    assert context.response.status_code == status_code, (
        f"Expected status {status_code}, got {context.response.status_code}. Response: {context.response.text}"
    )

@then('the response body should contain "Alert processing initiated"')
def step_impl(context):
    assert "Alert processing initiated" in context.response.text, (
        f'Expected "Alert processing initiated" in response, got {context.response.text}'
    )
