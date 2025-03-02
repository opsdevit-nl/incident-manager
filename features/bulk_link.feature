@bulk_link
Feature: Bulk Linking Main Alerts to an Incident

  Scenario: Successfully bulk link main alerts to an incident
    Given an incident with id "3" exists and is not discarded
    And main alerts with ids "301" and "302" exist and are not yet linked to incident "3"
    When a POST request is sent to "/incidents/3/bulk_link_main_alerts" with payload:
      """
      { "main_alert_ids": [301, 302], "last_modified_by": "user5" }
      """
    Then the response status should be 200
    And the response body should include "Bulk linking completed"

  Scenario: Fail to bulk link main alerts to a non-existent incident
    When a POST request is sent to "/incidents/999/bulk_link_main_alerts" with payload:
      """
      { "main_alert_ids": [301, 302], "last_modified_by": "user5" }
      """
    Then the response status should be 404
    And the response body should contain "Target incident not found"

  Scenario: Fail to bulk link main alerts to a discarded incident
    Given an incident with id "3" exists and is discarded
    When a POST request is sent to "/incidents/3/bulk_link_main_alerts" with payload:
      """
      { "main_alert_ids": [301, 302], "last_modified_by": "user5" }
      """
    Then the response status should be 400
    And the response body should contain "Cannot link main alerts to a discarded incident."
