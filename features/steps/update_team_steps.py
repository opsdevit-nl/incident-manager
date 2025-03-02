# update_team_steps.py
import os
import json
import requests
from behave import given, when, then

API_BASE = os.getenv("API_BASE", "http://backend:8000")

@given('an incident with id "15" exists with status "open"')
def step_impl_incident_15_exists(context):
    pass

@given('an incident with id "16" exists with status other than "open"')
def step_impl_incident_16_nonopen(context):
    pass

@when('a PATCH request is sent to "/incidents/15/update_team" with the payload')
def step_impl_update_team(context):
    url = f"{API_BASE}/incidents/15/update_team"
    payload = json.loads(context.text) if context.text else {}
    context.response = requests.patch(url, json=payload)

@when('a PATCH request is sent to "/incidents/16/update_team" with the payload')
def step_impl_update_team_nonopen(context):
    url = f"{API_BASE}/incidents/16/update_team"
    payload = json.loads(context.text) if context.text else {}
    context.response = requests.patch(url, json=payload)

@then('the incident team in the response should be "TAB"')
def step_impl_check_team(context):
    data = context.response.json()
    assert data.get("team") == "TAB"

@then('the response body should contain "Invalid team value"')
def step_impl_check_invalid_team(context):
    assert "Invalid team value" in context.response.text

@then('the response body should contain "Team can only be updated on open incidents"')
def step_impl_check_team_nonopen(context):
    assert "Team can only be updated on open incidents" in context.response.text
