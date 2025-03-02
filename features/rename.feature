@rename
Feature: Rename Incident

  Scenario: Successfully rename an incident
    Given an incident with id "12" exists
    When a PATCH request is sent to "/incidents/12/rename" with payload:
      """
      { "new_name": "New Incident Title", "last_modified_by": "user12" }
      """
    Then the response status should be 200
    And the incident name in the response should be "New Incident Title"

  Scenario: Fail to rename a non-existent incident
    When a PATCH request is sent to "/incidents/999/rename" with payload:
      """
      { "new_name": "New Name", "last_modified_by": "user12" }
      """
    Then the response status should be 404
    And the response body should contain "Incident not found"
