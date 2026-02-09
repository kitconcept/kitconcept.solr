context('Search Acceptance Tests (File)', () => {
  beforeEach(() => {
    // Docker compose setup requires host: solr-acceptance
    cy.setRegistry('collective.solr.host', 'solr-acceptance');
    cy.setRegistry('collective.solr.active', true);
    cy.setRegistry('collective.solr.use_tika', true);
    cy.reindexSolr();
  });
  afterEach(() => {
    cy.clearSolr();
  });
  // =========================================================================
  // FILE TITLE TERM SEARCH
  // =========================================================================
  //
  // Scenario: As anonymous user I can search for a file title
  //
  //   Given a public file with the title 'Colorless Green Ideas'
  //     and an anonymous user
  //    When I search for 'Colorless Green Ideas'
  //    Then the search returns '1' results
  //     and the search results should include 'Colorless Green Ideas'
  //
  it('File Title Search', function () {
    // GIVEN: a public file with the title 'Colorless Green Ideas'
    cy.createContent({
      contentType: 'File',
      contentId: 'colorless-green-ideas',
      contentTitle: 'Colorless Green Ideas',
      path: '',
    });
    // and an anonymous user
    cy.autologout();

    // WHEN: I search for 'Colorless'
    cy.visit('http://localhost:3000/search');
    cy.get('.search-input input').type('Colorless');
    cy.get('.search-input button').click();

    // THEN: the search returns '1' results
    cy.get('.total-bar .results').contains('1');
    // and the search results should include 'Colorless Green Ideas'
    cy.get('#content-core').contains('Colorless Green Ideas');
  });

  // =========================================================================
  // FILE DESCRIPTION TERM SEARCH
  // =========================================================================
  //
  // Scenario: As anonymous user I can search for a file description
  //
  //   Given a public file with the title 'Colorless Green Ideas' and the description 'Sleep Furiously'
  //     and an anonymous user
  //    When I search for 'Sleep Furiously'
  //    Then the search returns '1' results
  //     and the search results should include 'Colorless Green Ideas'
  //
  it('File Description Search', function () {
    // GIVEN: a public file with the title 'Colorless Green Ideas'
    // and the description 'Sleep Furiously'
    cy.createContent({
      contentType: 'File',
      contentId: 'colorless-green-ideas',
      contentTitle: 'Colorless Green Ideas',
      path: '',
      contentDescription: 'Sleep Furiously',
    });
    // and an anonymous user
    cy.autologout();

    // WHEN: I search for 'Sleep Furiously'
    cy.visit('http://localhost:3000/search');
    cy.get('.search-input input').type('Sleep Furiously');
    cy.get('.search-input button').click();

    // THEN: the search returns '1' results
    cy.get('.total-bar .results').contains('1');
    // and the search results should include 'Colorless Green Ideas'
    cy.get('#content-core').contains('Colorless Green Ideas');
  });

  // =========================================================================
  // FILE SUBJECTS (TAGS) SEARCH
  // =========================================================================
  //
  // Scenario: As anonymous user I can search for a file subject (tag)
  //
  //   Given a public file with the title 'Colorless Green Ideas' and the subject (tag) 'Sleep Furiously'
  //     and an anonymous user
  //    When I search for 'Sleep Furiously'
  //    Then the search returns '1' results
  //     and the search results should include 'Colorless Green Ideas'
  //
  it('File Subjects (Tags) Search', function () {
    // GIVEN: a public file with the title 'Colorless Green Ideas'
    // and the subject (tag) 'Sleep Furiously'
    cy.createContent({
      contentType: 'File',
      contentId: 'colorless-green-ideas',
      contentTitle: 'Colorless Green Ideas',
      path: '',
      contentSubjects: ['Furiously'],
    });
    // and an anonymous user
    cy.autologout();

    // WHEN: I search for 'Sleep Furiously'
    cy.visit('http://localhost:3000/search');
    cy.get('.search-input input').type('Furiously');
    cy.get('.search-input button').click();

    // THEN: the search returns '1' results
    cy.get('.total-bar .results').contains('1');
    // and the search results should include 'Colorless Green Ideas'
    cy.get('#content-core').contains('Colorless Green Ideas');
  });
});
