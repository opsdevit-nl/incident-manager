@audit_logs
Feature: Audit Logs Retrieval

  Scenario: Retrieve all audit logs without filters
    Given audit logs exist in the system
    When a GET request is sent to "/audit_logs/"
    Then the response status should be 200
    And the response body should include a list of audit logs

  Scenario: Retrieve audit logs filtered by date range
    Given audit logs exist with various timestamps
    When a GET request is sent to "/audit_logs/?from_date=2023-01-01T00:00:00&to_date=2023-12-31T23:59:59"
    Then the response status should be 200
    And each audit log's timestamp should be between "2023-01-01T00:00:00" and "2023-12-31T23:59:59"

  Scenario: Retrieve audit logs with an invalid date format
    When a GET request is sent to "/audit_logs/?from_date=invalid-date"
    Then the response status should be 400
    And the response body should contain "Invalid from_date format"
