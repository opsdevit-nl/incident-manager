@check_permission
Feature: Check Permission

  Scenario: Role with permission granted
    When a GET request is sent to "/check_permission/?role=admin"
    Then the response status should be 200
    And the response body should contain:
      """
      { "permission": "granted" }
      """

  Scenario: Role without permission denied
    When a GET request is sent to "/check_permission/?role=guest"
    Then the response status should be 403
    And the response body should contain "Permission denied"
