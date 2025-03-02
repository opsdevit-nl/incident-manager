@drag_link
Feature: Drag Linking a Main Alert

  Scenario: Successfully drag link a main alert to an incident
    Given an incident with id "1" exists and is not discarded
    And a main alert with id "102" exists and is not already linked to incident "1"
    When a POST request is sent to "/incidents/1/drag_link_main_alert/102" with payload:
      """
      { "last_modified_by": "user3" }
      """
    Then the response status should be 200
    And the response body should indicate the main alert has been transferred

  Scenario: Fail to drag link a main alert when the incident does not exist
    When a POST request is sent to "/incidents/999/drag_link_main_alert/102" with payload:
      """
      { "last_modified_by": "user3" }
      """
    Then the response status should be 404
    And the response body should contain "Target incident not found"

  Scenario: Fail to drag link a main alert if it belongs to a definitively resolved incident
    Given a main alert with id "102" is linked to an incident that is definitively resolved
    When a POST request is sent to "/incidents/1/drag_link_main_alert/102" with payload:
      """
      { "last_modified_by": "user3" }
      """
    Then the response status should be 400
    And the response body should contain "Cannot move main alert from a definitively resolved incident"
