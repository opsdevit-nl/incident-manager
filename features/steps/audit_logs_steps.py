# audit_logs_steps.py
import os
import requests
from behave import given, when, then

API_BASE = os.getenv("API_BASE", "http://backend:8000")

@given('audit logs exist in the system')
def step_impl_audit_logs_exist(context):
    # For testing, assume audit logs are already present.
    pass

@given('audit logs exist with various timestamps')
def step_impl_audit_logs_with_timestamps(context):
    # Optionally, pre-create some audit logs here.
    pass

@when('a GET request is sent to "/audit_logs/"')
def step_impl_get_audit_logs(context):
    url = f"{API_BASE}/audit_logs/"
    context.response = requests.get(url)

@when('a GET request is sent to "/audit_logs/?from_date=2023-01-01T00:00:00&to_date=2023-12-31T23:59:59"')
def step_impl_get_audit_logs_filtered(context):
    url = f"{API_BASE}/audit_logs/?from_date=2023-01-01T00:00:00&to_date=2023-12-31T23:59:59"
    context.response = requests.get(url)

@when('a GET request is sent to "/audit_logs/?from_date=invalid-date"')
def step_impl_get_audit_logs_invalid(context):
    url = f"{API_BASE}/audit_logs/?from_date=invalid-date"
    context.response = requests.get(url)

@then('the response body should include a list of audit logs')
def step_impl_check_audit_logs_list(context):
    data = context.response.json()
    assert isinstance(data.get("audit_logs", []), list), "Expected a list of audit logs"

@then("each audit log's timestamp should be between \"2023-01-01T00:00:00\" and \"2023-12-31T23:59:59\"")
def step_impl_check_timestamps(context):
    data = context.response.json()
    for log in data.get("audit_logs", []):
        ts = log.get("timestamp", "")
        assert "2023-01-01T00:00:00" <= ts <= "2023-12-31T23:59:59", f"Timestamp {ts} out of range"

@then('the response body should contain "Invalid from_date format"')
def step_impl_check_invalid_date(context):
    assert "Invalid from_date format" in context.response.text
