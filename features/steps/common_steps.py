# common_steps.py
import os
import json
import requests
from behave import then

# These common step definitions are used across multiple feature files.
# Ensure that no duplicate definitions exist in other step files.

@then('the response body should include a list of incidents')
def step_impl_check_incidents_list(context):
    data = context.response.json()
    assert isinstance(data.get("incidents", []), list)

@given('an incident with id "1" exists and is not discarded')
def step_impl_incident_1_exists(context):
    pass  # Assume incident 1 exists

@then('the response body should contain "Target incident not found"')
def step_impl_target_incident_not_found(context):
    assert "Target incident not found" in context.response.text, (
        f"Expected 'Target incident not found' in response, got: {context.response.text}"
    )

@then('the response body should contain "Invalid JSON payload"')
def step_impl_invalid_json_payload(context):
    assert "Invalid JSON payload" in context.response.text, (
        f"Expected 'Invalid JSON payload' in response, got: {context.response.text}"
    )

@then('the response body should contain "Permission denied"')
def step_impl_permission_denied(context):
    assert "Permission denied" in context.response.text, (
        f"Expected 'Permission denied' in response, got: {context.response.text}"
    )

@then('the response body should contain "Cannot link main alerts to a discarded incident."')
def step_impl_cannot_link_discarded(context):
    assert "Cannot link main alerts to a discarded incident." in context.response.text, (
        f"Expected 'Cannot link main alerts to a discarded incident.' in response, got: {context.response.text}"
    )

@then('the response body should contain "Main alert already linked to this incident"')
def step_impl_main_alert_already_linked(context):
    assert "Main alert already linked to this incident" in context.response.text, (
        f"Expected 'Main alert already linked to this incident' in response, got: {context.response.text}"
    )

@then('the response body should contain "Comment not found"')
def step_impl_comment_not_found(context):
    assert "Comment not found" in context.response.text, (
        f"Expected 'Comment not found' in response, got: {context.response.text}"
    )

@then('the response body should contain "Comment deleted"')
def step_impl_comment_deleted(context):
    assert "Comment deleted" in context.response.text, (
        f"Expected 'Comment deleted' in response, got: {context.response.text}"
    )

@then('the response body should contain "Incident not found"')
def step_impl_incident_not_found(context):
    assert "Incident not found" in context.response.text, (
        f"Expected 'Incident not found' in response, got: {context.response.text}"
    )

@then('the response body should contain "Main alerts resolved"')
def step_impl_main_alerts_resolved(context):
    assert "Main alerts resolved" in context.response.text, (
        f"Expected 'Main alerts resolved' in response, got: {context.response.text}"
    )

@then('the response body should contain "Bulk linking completed"')
def step_impl_bulk_linking_completed(context):
    assert "Bulk linking completed" in context.response.text, (
        f"Expected 'Bulk linking completed' in response, got: {context.response.text}"
    )

@then('the response body should contain "Undo drag of main alert completed"')
def step_impl_undo_drag_completed(context):
    assert "Undo drag of main alert completed" in context.response.text, (
        f"Expected 'Undo drag of main alert completed' in response, got: {context.response.text}"
    )

@then('the response body should include "Undo drag transfer completed"')
def step_impl_undo_drag_transfer_completed(context):
    assert "Undo drag transfer completed" in context.response.text, (
        f"Expected 'Undo drag transfer completed' in response, got: {context.response.text}"
    )
