context('Search Acceptance Tests (Document)', () => {
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
  // DOCUMENT TITLE TERM SEARCH
  // =========================================================================
  //
  // Scenario: As anonymous user I can search for a document title
  //
  //   Given a public document with the title 'Colorless'
  //     and an anonymous user
  //    When I search for 'Colorless'
  //    Then the search returns '1' results
  //     and the search results should include 'Colorless'
  //
  it('Page Title Search', function () {
    // GIVEN: a public document with the title 'Colorless'
    cy.createContent({
      contentType: 'Document',
      contentId: 'colorless',
      contentTitle: 'Colorless',
      path: '',
    });
    // cy.setWorkflow({
    //   path: '/colorless-green-ideas',
    //   workflow_state: 'published',
    // });
    cy.request({
      method: 'POST',
      url: `http://localhost:55001/plone/colorless/@workflow/publish`,
      headers: {
        Accept: 'application/json',
      },
      auth: {
        user: 'admin',
        pass: 'secret',
      },
    });
    // and an anonymous user
    cy.autologout();

    // WHEN: I search for 'Colorless'
    cy.visit('http://localhost:3000/search');
    cy.get('.searchinput').type('Colorless');
    cy.get('.search-input button').click();

    // THEN: the search returns '1' results
    cy.get('.total-bar .results').contains('1');
    // and the search results should include 'Colorless'
    cy.get('#content-core').contains('Colorless');
  });

  // =========================================================================
  // DOCUMENT DESCRIPTION TERM SEARCH
  // =========================================================================
  //
  // Scenario: As anonymous user I can search for a document description
  //
  //   Given a public document with the title 'Colorless Green Ideas'
  //     and the description 'Sleep Furiously'
  //     and an anonymous user
  //    When I search for 'Sleep Furiously'
  //    Then the search returns '1' results
  //     and the search results should include 'Colorless Green Ideas'
  //
  it('Description Term Search', function () {
    // Given a public document with the title 'Colorless Green Ideas'
    //   and the description 'Sleep Furiously'
    cy.createContent({
      contentType: 'Document',
      contentId: 'colorless-green-ideas',
      contentTitle: 'Colorless Green Ideas',
      contentDescription: 'Sleep Furiously',
      path: '',
    });
    // cy.setWorkflow({
    //   path: '/colorless-green-ideas',
    //   workflow_state: 'published',
    // });
    cy.request({
      method: 'POST',
      url: `http://localhost:55001/plone/colorless-green-ideas/@workflow/publish`,
      headers: {
        Accept: 'application/json',
      },
      auth: {
        user: 'admin',
        pass: 'secret',
      },
    });
    // and an anonymous user
    cy.autologout();

    // WHEN: I search for 'Sleep Furiously'
    cy.visit('http://localhost:3000/search');
    cy.get('.searchinput').type('Sleep Furiously');
    cy.get('.search-input button').click();

    // THEN: the search returns '1' results
    cy.get('.total-bar .results').contains('1');
    // and the search results should include 'Colorless Green Ideas'
    cy.get('#content-core').contains('Colorless Green Ideas');
  });

  // =========================================================================
  // DOCUMENT TAGS SEARCH
  // =========================================================================
  //
  // Scenario: As anonymous user I can search for a document tag
  //
  //   Given a public document with the title 'Colorless Green Ideas'
  //     and the tag 'Furiously'
  //     and an anonymous user
  //    When I search for 'Furiously'
  //    Then the search returns '1' results
  //     and the search results should include 'Colorless Green Ideas'
  //
  it('Page Tag Search', function () {
    // Given a public document with the title 'Colorless Green Ideas'
    //   and the tag 'Furiously'
    cy.createContent({
      contentType: 'Document',
      contentId: 'colorless-green-ideas',
      contentTitle: 'Colorless Green Ideas',
      contentSubjects: ['Furiously'],
      path: '',
    });
    // cy.setWorkflow({
    //   path: '/colorless-green-ideas',
    //   workflow_state: 'published',
    // });
    cy.request({
      method: 'POST',
      url: `http://localhost:55001/plone/colorless-green-ideas/@workflow/publish`,
      headers: {
        Accept: 'application/json',
      },
      auth: {
        user: 'admin',
        pass: 'secret',
      },
    });

    // and an anonymous user
    cy.autologout();

    // WHEN: I search for 'Sleep Furiously'
    cy.visit('http://localhost:3000/search');
    cy.get('.searchinput').type('Furiously');
    cy.get('.search-input button').click();

    // THEN: the search returns '1' results
    cy.get('.total-bar .results').contains('1');
    // and the search results should include 'Colorless Green Ideas'
    cy.get('#content-core').contains('Colorless Green Ideas');
  });
});
