@undo_drag_link
Feature: Undo Drag Linking a Main Alert

  Scenario: Successfully undo the drag link of a main alert
    Given an incident with id "1" exists and a main alert with id "102" is linked to it
    When a POST request is sent to "/incidents/1/undo_drag_link_main_alert/102" with payload:
      """
      { "last_modified_by": "user3" }
      """
    Then the response status should be 200
    And the response body should contain "Undo drag of main alert completed"

  Scenario: Fail to undo drag link when the source incident does not exist
    When a POST request is sent to "/incidents/999/undo_drag_link_main_alert/102" with payload:
      """
      { "last_modified_by": "user3" }
      """
    Then the response status should be 404
    And the response body should contain "Source incident not found"
