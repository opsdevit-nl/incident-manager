@read_incidents
Feature: Read Incidents

  Scenario: Retrieve incidents with default filters
    Given multiple incidents exist in the system
    When a GET request is sent to "/incidents/"
    Then the response status should be 200
    And the response body should include a list of incidents

  Scenario: Retrieve incidents with filtering, sorting, and pagination
    When a GET request is sent to "/incidents/?status=resolved&team=TAB&page=2&limit=5&sort_by=incident_name&sort_order=asc"
    Then the response status should be 200
    And the incidents in the response should match the filter criteria
