@create_incident
Feature: Create Incident

  Scenario: Successfully create an incident
    Given a valid incident payload:
      """
      { "incident_name": "Network Outage", "host": "router1" }
      """
    When a POST request is sent to "/incidents/" with the payload
    Then the response status should be 200
    And the response body should include an incident with the name "Network Outage"

  Scenario: Fail to create an incident with missing required fields
    Given an incident payload missing required fields
    When a POST request is sent to "/incidents/" with the payload
    Then the response status should be 400
