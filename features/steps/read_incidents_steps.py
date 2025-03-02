# read_incidents_steps.py
import os
import requests
from behave import given, when, then

API_BASE = os.getenv("API_BASE", "http://backend:8000")

@given('multiple incidents exist in the system')
def step_impl_multiple_incidents_exist(context):
    # Optionally create multiple incidents via API if needed.
    pass

@when('a GET request is sent to "/incidents/"')
def step_impl_get_incidents(context):
    url = f"{API_BASE}/incidents/"
    context.response = requests.get(url)

@when('a GET request is sent to "/incidents/?status=resolved&team=TAB&page=2&limit=5&sort_by=incident_name&sort_order=asc"')
def step_impl_get_incidents_filtered(context):
    url = f"{API_BASE}/incidents/?status=resolved&team=TAB&page=2&limit=5&sort_by=incident_name&sort_order=asc"
    context.response = requests.get(url)



@then('the incidents in the response should match the filter criteria')
def step_impl_check_filtered_incidents(context):
    data = context.response.json()
    for inc in data.get("incidents", []):
        assert inc.get("status") in ["resolved", "def-resolved"], "Incident status mismatch"
        assert inc.get("team") == "TAB", "Incident team mismatch"
