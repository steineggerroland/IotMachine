Feature: Showing general information of virtual entities

  Scenario: All virtual entity types are present
    Given the user goes to the virtual entities page
    Then they see rooms in the room catalog
    And they see appliances in the appliance depot
    And they see person in the register of persons

  Scenario: The user sees all rooms
    Given the user goes to the virtual entities page
    Then they see the rooms Bathroom, Living room, Parents bedroom, Kitchen, Terrace

  Scenario: The user sees all appliances
    Given the user goes to the virtual entities page
    Then they see the appliances Dishwasher, Dryer

  Scenario: The user sees all persons
    Given the user goes to the virtual entities page
    Then they see the persons Robin, Ash

  Scenario: Power consumption updates are displayed
    Given the user goes to the virtual entities page
    When the power consumption of the Dryer is updated
    Then the user sees the new power consumption for the Dryer after a refresh

  Scenario: Room climate updates are displayed
    Given the user goes to the virtual entities page
    When the room climate of the Kitchen is updated
    Then the user sees the new temperature for the Kitchen after a refresh
    And the user sees the new humidity for the Kitchen after a refresh
