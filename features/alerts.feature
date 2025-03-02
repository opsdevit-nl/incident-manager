@alerts
Feature: Alerts Processing

  Scenario: Create alerts with a valid bulk payload
    Given a valid bulk alerts payload:
      """
      {
        "alerts": [
          {
            "status": "new",
            "labels": { "alertname": "CPU_Alert", "destination": "pls", "host": "server1" },
            "annotations": { "description": "High CPU usage" }
          }
        ],
        "externalURL": "http://example.com",
        "last_modified_by": "user1"
      }
      """
    When a POST request is sent to "/alerts/" with the payload
    Then the response status should be 200
    And the response body should contain "Alert processing initiated"

  Scenario: Create alerts with an invalid JSON payload
    Given an invalid JSON payload
    When a POST request is sent to "/alerts/"
    Then the response status should be 400
    And the response body should contain "Invalid JSON payload"

  Scenario: Create legacy alerts (non-bulk)
    Given a legacy alert payload:
      """
      {
        "message": "Legacy alert message",
        "source": "tab",
        "host": "server2",
        "state": "1",
        "wikilink": "Undefined",
        "status": "new"
      }
      """
    When a POST request is sent to "/alerts/" with the payload
    Then the response status should be 200
    And the response body should contain "Alert processing initiated"
