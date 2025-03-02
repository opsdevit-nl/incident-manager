@resolution
Feature: Incident Resolution and Reopening

  Scenario: Manually resolve an incident
    Given an incident with id "8" exists
    When a PATCH request is sent to "/incidents/8/resolve" with payload:
      """
      { "last_modified_by": "user9" }
      """
    Then the response status should be 200
    And the incident status in the response should be "resolved"

  Scenario: Definitively resolve an incident
    Given an incident with id "9" exists
    When a PATCH request is sent to "/incidents/9/definitively_resolve" with payload:
      """
      { "last_modified_by": "user10" }
      """
    Then the response status should be 200
    And the incident status in the response should be "def-resolved"
    And the "definitively_resolved" flag should be true

  Scenario: Fail to resolve a non-existent incident
    When a PATCH request is sent to "/incidents/999/resolve" with payload:
      """
      { "last_modified_by": "user9" }
      """
    Then the response status should be 404
    And the response body should contain "Incident not found"

  Scenario: Reopen an incident that is resolved but not definitively resolved
    Given an incident with id "10" exists with status "resolved"
    When a PATCH request is sent to "/incidents/10/reopen" with payload:
      """
      { "last_modified_by": "user11" }
      """
    Then the response status should be 200
    And the incident status in the response should be "open"

  Scenario: Fail to reopen a definitively resolved incident
    Given an incident with id "11" exists and is definitively resolved
    When a PATCH request is sent to "/incidents/11/reopen" with payload:
      """
      { "last_modified_by": "user11" }
      """
    Then the response status should be 400
    And the response body should contain "Incident is definitively resolved and cannot be reopened"
