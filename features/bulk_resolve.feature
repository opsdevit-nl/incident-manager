@bulk_resolve
Feature: Bulk Resolving Main Alerts

  Scenario: Successfully bulk resolve main alerts
    Given main alerts with ids "201" and "202" exist
    When a PATCH request is sent to "/main_alerts/bulk_resolve" with payload:
      """
      { "main_alert_ids": [201, 202], "last_modified_by": "user4" }
      """
    Then the response status should be 200
    And the response body should contain "Main alerts resolved"
