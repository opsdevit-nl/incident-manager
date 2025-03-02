@link_main_alert
Feature: Linking a Main Alert to an Incident

  Scenario: Successfully link a main alert to an existing incident
    Given an incident with id "1" exists and is not discarded
    And a main alert with id "101" exists
    When a POST request is sent to "/incidents/1/link_main_alert" with payload:
      """
      { "main_alert_id": 101, "last_modified_by": "user2" }
      """
    Then the response status should be 200
    And the response body should include "Main alert linked to target incident"

  Scenario: Fail to link a main alert to a non-existent incident
    When a POST request is sent to "/incidents/999/link_main_alert" with payload:
      """
      { "main_alert_id": 101, "last_modified_by": "user2" }
      """
    Then the response status should be 404
    And the response body should contain "Target incident not found"

  Scenario: Fail to link a main alert to a discarded incident
    Given an incident with id "2" exists and its status is "discarded"
    When a POST request is sent to "/incidents/2/link_main_alert" with payload:
      """
      { "main_alert_id": 101, "last_modified_by": "user2" }
      """
    Then the response status should be 400
    And the response body should contain "Cannot link a main alert to a discarded incident"

  Scenario: Linking a main alert that is already linked to the incident
    Given an incident with id "1" exists and already has main alert id "101" linked
    When a POST request is sent to "/incidents/1/link_main_alert" with payload:
      """
      { "main_alert_id": 101, "last_modified_by": "user2" }
      """
    Then the response status should be 200
    And the response body should contain "Main alert already linked to this incident"
