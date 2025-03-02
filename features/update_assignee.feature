@update_assignee
Feature: Update Incident Assignee

  Scenario: Successfully update assignee on an open incident
    Given an incident with id "17" exists with status "open"
    When a PATCH request is sent to "/incidents/17/update_assignee" with payload:
      """
      { "assignee": "Ted", "last_modified_by": "user17" }
      """
    Then the response status should be 200
    And the incident assignee in the response should be "Ted"

  Scenario: Fail to update assignee with an invalid value
    When a PATCH request is sent to "/incidents/17/update_assignee" with payload:
      """
      { "assignee": "Unknown", "last_modified_by": "user17" }
      """
    Then the response status should be 400
    And the response body should contain "Invalid assignee value"

  Scenario: Fail to update assignee on a non-open incident
    Given an incident with id "18" exists with status other than "open"
    When a PATCH request is sent to "/incidents/18/update_assignee" with payload:
      """
      { "assignee": "Linda", "last_modified_by": "user18" }
      """
    Then the response status should be 400
    And the response body should contain "Assignee can only be updated on open incidents"
