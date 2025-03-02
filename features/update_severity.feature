@update_severity
Feature: Update Incident Severity

  Scenario: Successfully update severity on an open incident
    Given an incident with id "13" exists with status "open"
    When a PATCH request is sent to "/incidents/13/update_severity" with payload:
      """
      { "severity": "HIGH", "last_modified_by": "user13" }
      """
    Then the response status should be 200
    And the incident severity in the response should be "HIGH"

  Scenario: Fail to update severity with an invalid value
    When a PATCH request is sent to "/incidents/13/update_severity" with payload:
      """
      { "severity": "CRITICAL", "last_modified_by": "user13" }
      """
    Then the response status should be 400
    And the response body should contain "Invalid severity value"

  Scenario: Fail to update severity on a non-open incident
    Given an incident with id "14" exists with status other than "open"
    When a PATCH request is sent to "/incidents/14/update_severity" with payload:
      """
      { "severity": "LOW", "last_modified_by": "user14" }
      """
    Then the response status should be 400
    And the response body should contain "Severity can only be updated on open incidents"
