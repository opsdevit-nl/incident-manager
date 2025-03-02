# create_incident_steps.py
import os
import json
import requests
from behave import given, when, then

API_BASE = os.getenv("API_BASE", "http://backend:8000")

@given('a valid incident payload')
def step_impl_valid_incident_payload(context):
    context.payload = {"incident_name": "Network Outage", "host": "router1"}

@given('an incident payload missing required fields')
def step_impl_invalid_incident_payload(context):
    context.payload = {"host": "router1"}  # missing incident_name

@when('a POST request is sent to "/incidents/" with the payload')
def step_impl_create_incident(context):
    url = f"{API_BASE}/incidents/"
    context.response = requests.post(url, json=context.payload)

@then('the response body should include an incident with the name "Network Outage"')
def step_impl_check_incident_created(context):
    data = context.response.json()
    assert data.get("incident_name") == "Network Outage", f"Got {data.get('incident_name')}"

# @then('the response body should include a list of incidents')
# def step_impl_check_incidents_list(context):
#     data = context.response.json()
#     assert isinstance(data.get("incidents", []), list)
