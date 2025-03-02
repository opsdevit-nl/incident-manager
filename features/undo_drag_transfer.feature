@undo_drag_transfer
Feature: Undo Drag Transfer of an Incident

  Scenario: Successfully undo a drag transfer
    Given incidents with ids "5" (source) and "6" (target) exist and a transfer has been performed
    And main alerts with ids [501, 502] were transferred from incident "5" to incident "6"
    When a POST request is sent to "/incidents/6/undo_drag_transfer/5" with payload:
      """
      { "main_alert_ids": [501, 502], "last_modified_by": "user8" }
      """
    Then the response status should be 200
    And the response body should include "Undo drag transfer completed"
