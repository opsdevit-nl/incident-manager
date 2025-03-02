@update_team
Feature: Update Incident Team

  Scenario: Successfully update team on an open incident
    Given an incident with id "15" exists with status "open"
    When a PATCH request is sent to "/incidents/15/update_team" with payload:
      """
      { "team": "TAB", "last_modified_by": "user15" }
      """
    Then the response status should be 200
    And the incident team in the response should be "TAB"

  Scenario: Fail to update team with an invalid value
    When a PATCH request is sent to "/incidents/15/update_team" with payload:
      """
      { "team": "InvalidTeam", "last_modified_by": "user15" }
      """
    Then the response status should be 400
    And the response body should contain "Invalid team value"

  Scenario: Fail to update team on a non-open incident
    Given an incident with id "16" exists with status other than "open"
    When a PATCH request is sent to "/incidents/16/update_team" with payload:
      """
      { "team": "Hades", "last_modified_by": "user16" }
      """
    Then the response status should be 400
    And the response body should contain "Team can only be updated on open incidents"
