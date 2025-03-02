@comments
Feature: Incident Comments Management

  Scenario: Add a comment to an incident
    Given an incident with id "4" exists
    When a POST request is sent to "/incidents/4/comments/" with payload:
      """
      { "login_name": "user6", "comment_text": "This incident needs attention" }
      """
    Then the response status should be 200
    And the response body should include the comment details with "user6" as the login name

  Scenario: Update a comment on an incident
    Given a comment with id "401" exists on incident "4"
    When a PATCH request is sent to "/incidents/4/comments/401" with payload:
      """
      { "comment_text": "Updated comment text" }
      """
    Then the response status should be 200
    And the response body should reflect the updated comment text

  Scenario: Delete a comment from an incident
    Given a comment with id "402" exists on incident "4"
    When a DELETE request is sent to "/incidents/4/comments/402"
    Then the response status should be 200
    And the response body should contain "Comment deleted"

  Scenario: Fail to update a non-existent comment
    When a PATCH request is sent to "/incidents/4/comments/999" with payload:
      """
      { "comment_text": "Updated text" }
      """
    Then the response status should be 404
    And the response body should contain "Comment not found"

  Scenario: Fail to delete a non-existent comment
    When a DELETE request is sent to "/incidents/4/comments/999"
    Then the response status should be 404
    And the response body should contain "Comment not found"
