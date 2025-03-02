@drag_transfer
Feature: Drag Transfer of an Incident

  Scenario: Successfully drag transfer an incident
    Given two incidents exist with ids "5" (source) and "6" (target) where the target is not discarded
    When a POST request is sent to "/incidents/6/drag_transfer/5" with payload:
      """
      { "last_modified_by": "user7" }
      """
    Then the response status should be 200
    And the response body should include "Incident transferred via drag & drop"

  Scenario: Fail to drag transfer when the source incident does not exist
    When a POST request is sent to "/incidents/6/drag_transfer/999" with payload:
      """
      { "last_modified_by": "user7" }
      """
    Then the response status should be 404
    And the response body should contain "Incident not found"

  Scenario: Fail to drag transfer into a discarded incident
    Given an incident with id "7" exists and is discarded
    When a POST request is sent to "/incidents/7/drag_transfer/5" with payload:
      """
      { "last_modified_by": "user7" }
      """
    Then the response status should be 400
    And the response body should contain "Cannot transfer into a discarded incident"
