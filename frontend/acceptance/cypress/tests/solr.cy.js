context('Search Acceptance Tests (Features)', () => {
  beforeEach(() => {
    // Docker compose setup requires host: solr-acceptance
    cy.setRegistry('collective.solr.host', 'solr-acceptance');
    cy.setRegistry('collective.solr.active', true);
    cy.reindexSolr();
  });
  afterEach(() => {
    cy.clearSolr();
  });

  // =========================================================================
  // TITLE TERM SEARCH
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
  it('Title Term Search', function () {
    // GIVEN: a public document with the title 'Colorless'
    cy.createContent({
      contentType: 'Document',
      contentId: 'colorless',
      contentTitle: 'Colorless',
      path: '/',
    });
    // cy.setWorkflow({
    //   path: '//colorless-green-ideas',
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
  // DESCRIPTION TERM SEARCH
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
      path: '/',
    });
    // cy.setWorkflow({
    //   path: '//colorless-green-ideas',
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
  // PDF FILE CONTENTSEARCH
  // =========================================================================
  //
  // Scenario: As anonymous user I can find a term within a PDF document
  //
  //   Given a public PDF file that contains 'Lorem ipsum'
  //     and an anonymous user
  //    When I search for 'Lorem ipsum'
  //    Then the search returns '1' results
  //     and the search results should include 'Lorem ipsum'
  //
  it('PDF Content Search', function () {
    // GIVEN: a public PDF file that contains 'Lorem ipsum'
    cy.createPDF();

    // WHEN: I search for 'Lorem ipsum'
    cy.visit('http://localhost:3000/search');
    cy.get('.searchinput').type('Lorem ipsum');
    cy.get('.search-input button').click();

    // THEN: the search returns '1' results
    cy.get('.total-bar .results').contains('1');
    // and the search results should include 'Colorless'
    cy.get('#content-core').contains('Lorem ipsum');
  });

  // =========================================================================
  // CASE INSENSITIVE SEARCH (#6) Upper -> Lower
  // =========================================================================
  //
  // Scenario: As anonymous user I can find a term insensitive to the case used
  //
  //   Given a public document with the title 'Colorless Green Ideas'
  //     and an anonymous user
  //    When I search for 'colorless green ideas'
  //    Then the search returns '1' results
  //     and the search results should include 'Colorless Green Ideas'
  //
  it('Case Insensitive Search (Upper -> Lower)', function () {
    // GIVEN: a public document with the title 'Colorless Green Ideas'
    cy.createContent({
      contentType: 'Document',
      contentId: 'colorless-green-ideas',
      contentTitle: 'Colorless Green Ideas',
      path: '/',
    });
    // cy.setWorkflow({
    //   path: '//colorless-green-ideas',
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

    // WHEN: I search for 'Colorless Green Ideas'
    cy.visit('http://localhost:3000/search');
    cy.get('.searchinput').type('colorless green ideas');
    cy.get('.search-input button').click();

    // THEN: the search returns '1' results
    cy.get('.total-bar .results').contains('1');
    // and the search results should include 'Colorless Green Ideas'
    cy.get('#content-core').contains('Colorless Green Ideas');
  });

  // =========================================================================
  // CASE INSENSITIVE SEARCH (#6) Lower -> Upper
  // =========================================================================
  //
  // Scenario: As anonymous user I can find a term insensitive to the case used
  //
  //   Given a public document with the title 'Colorless Green Ideas'
  //     and an anonymous user
  //    When I search for 'colorless green ideas'
  //    Then the search returns '1' results
  //     and the search results should include 'Colorless Green Ideas'
  //
  it('Case Insensitive Search (Lower -> Upper)', function () {
    // GIVEN: a public document with the title 'colorless green ideas'
    cy.createContent({
      contentType: 'Document',
      contentId: 'colorless-green-ideas',
      contentTitle: 'colorless green ideas',
      path: '/',
    });
    // cy.setWorkflow({
    //   path: '//colorless-green-ideas',
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

    // WHEN: I search for 'Colorless Green Ideas'
    cy.visit('http://localhost:3000/search');
    cy.get('.searchinput').type('Colorless Green Ideas');
    cy.get('.search-input button').click();

    // THEN: the search returns '1' results
    cy.get('.total-bar .results').contains('1');
    // and the search results should include 'Colorless Green Ideas'
    cy.get('#content-core').contains('colorless green ideas');
  });

  // =========================================================================
  // SEARCH TERM HIGHLIGHTING
  // =========================================================================
  //
  // Scenario: As anonymous user I can see my search term highlighted in the search results
  //
  //   Given a public document with the title 'Colorless'
  //     and the description 'Colorless green ideas sleep furiously'
  //     and an anonymous user
  //    When I search for 'green ideas'
  //    Then the search returns '1' results
  //     and the search results should include 'Colorless green ideas sleep furiously'
  //     and the search results should highlight 'green ideas'
  it('Search Term Highlighting', function () {
    // Given a public document with the title 'Colorless'
    //   and the description 'Colorless green ideas sleep furiously'
    cy.createContent({
      contentType: 'Document',
      contentId: 'colorless',
      contentTitle: 'Colorless',
      contentText: 'Colorless green ideas sleep furiously',
      path: '/',
    });
    // cy.setWorkflow({
    //   path: '//colorless-green-ideas',
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

    // WHEN: I search for 'green ideas'
    cy.visit('http://localhost:3000/search');
    cy.get('.searchinput').type('green');
    cy.get('.search-input button').click();

    // THEN: the search returns '1' results
    cy.get('.total-bar .results').contains('1');
    // and the search results should include 'Colorless'
    cy.get('#content-core').contains('Colorless');
    // and the search results should include 'Colorless green ideas sleep furiously'
    cy.get('#content-core').contains('Colorless green ideas sleep furiously');
    // and the search results should highlight 'green'
    cy.get('#content-core .description em').contains('green');
  });

  // =========================================================================
  // PREFIX SEARCH (#3)
  // =========================================================================
  //
  // Scenario: As anonymous user I can search for a term prefix in the document title
  //
  // Given a public document with the title 'Colorless Green Ideas'
  //   and an anonymous user
  //  When I search for 'Color'
  //   Then the search returns '1' results
  //   and the search results should include 'Colorless Green Ideas'
  //
  it('Prefix Search', function () {
    // GIVEN: a public document with the title 'Colorless Green Ideas'
    cy.createContent({
      contentType: 'Document',
      contentId: 'colorless-green-ideas',
      contentTitle: 'Colorless Green Ideas',
      path: '/',
    });
    // cy.setWorkflow({
    //   path: '//colorless-green-ideas',
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

    // WHEN: I search for 'Color'
    cy.visit('http://localhost:3000/search');
    cy.get('.searchinput').type('Color');
    cy.get('.search-input button').click();

    // THEN: the search returns '1' results
    cy.get('.total-bar .results').contains('1');
    // and the search results should include 'Colorless Green Ideas'
    cy.get('#content-core').contains('Colorless Green Ideas');
  });

  // =========================================================================
  // SUFFIX SEARCH
  // =========================================================================
  //
  // Scenario: As anonymous user I can search for a term suffix in the document title
  //
  // Given a public document with the title 'Colorless Green Ideas'
  //   and an anonymous user
  //  When I search for 'less'
  //   Then the search returns '1' results
  //   and the search results should include 'Colorless Green Ideas'
  //
  it('Suffix Search', function () {
    // GIVEN: a public document with the title 'Colorless Green Ideas'
    cy.createContent({
      contentType: 'Document',
      contentId: 'colorless-green-ideas',
      contentTitle: 'Colorless Green Ideas',
      path: '/',
    });
    // cy.setWorkflow({
    //   path: '//colorless-green-ideas',
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

    // WHEN: I search for 'less'
    cy.visit('http://localhost:3000/search');
    cy.get('.searchinput').type('less');
    cy.get('.search-input button').click();

    // THEN: the search returns '1' results
    cy.get('.total-bar .results').contains('1');
    // and the search results should include 'Colorless Green Ideas'
    cy.get('#content-core').contains('Colorless Green Ideas');
  });

  // // =========================================================================
  // // SUBSTRING SEARCH
  // // =========================================================================
  // //
  // // Scenario: As anonymous user I can search for a term substring in the document title
  // //
  // // Given a public document with the title 'Colorless Green Ideas'
  // //   and an anonymous user
  // //  When I search for 'lorless'
  // //  Then the search returns '1' results
  // //   and the search results should include 'Colorless Green Ideas'
  // // -> https://jugit.fz-juelich.de/fzj-internet/dlr/-/issues/5
  // //
  // it('Substring Search', function () {
  //   // Given a public document with the title 'Colorless Green Ideas'
  //   //   and the description 'Sleep Furiously'
  //   cy.createContent({
  //     contentType: 'Document',
  //     contentId: 'colorless-green-ideas',
  //     contentTitle: 'Colorless Green Ideas',
  //     contentDescription: 'Sleep Furiously',
  //     path: '/',
  //   });
  //   // cy.setWorkflow({
  //   //   path: '//colorless-green-ideas',
  //   //   workflow_state: 'published',
  //   // });
  //   cy.request({
  //     method: 'POST',
  //     url: `http://localhost:55001/plone/colorless-green-ideas/@workflow/publish`,
  //     headers: {
  //       Accept: 'application/json',
  //     },
  //     auth: {
  //       user: 'admin',
  //       pass: 'secret',
  //     },
  //   });
  //   // and an anonymous user
  //   cy.autologout();

  //   // WHEN: I search for 'lorless'
  //   cy.visit('http://localhost:3000/search');
  //   cy.get('.searchinput').type('lorless');
  //   cy.get('.search-input button').click();

  //   // THEN: the search returns '1' results
  //   cy.get('.total-bar .results').contains('1');
  //   // and the search results should include 'Colorless Green Ideas'
  //   cy.get('#content-core').contains('Colorless Green Ideas');
  // });

  // =========================================================================
  // SYNONYM SEARCH (#8)
  // =========================================================================
  //
  // Scenario: As anonymous user I can find a term when searching for one of its synonyms
  //
  // Given a public document with the title 'House'
  //   and an anonymous user
  //  When I search for 'Residence'
  //  Then the search returns '1' results
  //   and the search results should include 'House'
  // -> https://jugit.fz-juelich.de/fzj-internet/dlr/-/issues/8
  //
  it('Synonym Search', function () {
    // Given a public document with the title 'House'
    cy.createContent({
      contentType: 'Document',
      contentId: 'house',
      contentTitle: 'House',
      path: '/',
    });
    // cy.setWorkflow({
    //   path: '//colorless-green-ideas',
    //   workflow_state: 'published',
    // });
    cy.request({
      method: 'POST',
      url: `http://localhost:55001/plone/house/@workflow/publish`,
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

    // WHEN: I search for 'Residence'
    cy.visit('http://localhost:3000/search');
    cy.get('.searchinput').type('Residence');
    cy.get('.search-input button').click();

    // THEN: the search returns '1' results
    cy.get('.total-bar .results').contains('1');
    // and the search results should include 'House'
    cy.get('#content-core').contains('House');
  });

  // =========================================================================
  // PHRASE SEARCH (#7)
  // =========================================================================
  //
  // Scenario: As anonymous user I can search for a phrase in a Page title
  //
  //   Given a public document with the title 'Colorless Green Ideas'
  //     and an anonymous user
  //    When I search for 'Colorless Green Ideas'
  //    Then the search returns '1' results
  //     and the search results should include 'Colorless Green Ideas'
  //
  it('Phrase Search', function () {
    // GIVEN: a public document with the title 'Colorless Green Ideas'
    cy.createContent({
      contentType: 'Document',
      contentId: 'colorless-green-ideas',
      contentTitle: 'Colorless Green Ideas',
      path: '/',
    });
    // cy.setWorkflow({
    //   path: '//colorless-green-ideas',
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

    // WHEN: I search for 'Colorless Green Ideas'
    cy.visit('http://localhost:3000/search');
    cy.get('.searchinput').type('Colorless Green Ideas');
    cy.get('.search-input button').click();

    // THEN: the search returns '1' results
    cy.get('.total-bar .results').contains('1');
    // and the search results should include 'Colorless Green Ideas'
    cy.get('#content-core').contains('Colorless Green Ideas');
  });

  it('Language dependent', function () {
    cy.createContent({
      contentType: 'Document',
      contentId: 'colorless',
      contentTitle: 'Colorless',
      path: '/',
    });
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
    cy.autologout();
    cy.createContent({
      contentType: 'Document',
      contentId: 'colorless',
      contentTitle: 'Colorless German',
      path: '/de',
      language: 'de',
    });
    cy.request({
      method: 'POST',
      url: `http://localhost:55001/plone/de/colorless/@workflow/publish`,
      headers: {
        Accept: 'application/json',
      },
      auth: {
        user: 'admin',
        pass: 'secret',
      },
    });
    cy.autologout();

    // This only works in @@search. Caveat - Old usage search is deprecated and
    // although works, does not support this switch.
    cy.visit('http://localhost:3000/@@search');
    cy.get('.searchinput').type('Colorless');
    cy.get('.search-input button').click();

    cy.get('.total-bar .results').contains('1');
    cy.get('#content-core').contains('Colorless');

    cy.intercept('GET', '/plone/++api++/@solr*').as('solr');
    cy.get('.language-selector').contains('de').click();
    cy.wait('@solr');

    cy.get('.total-bar .results').contains('1');
    cy.get('#content-core').contains('Colorless German');
  });
});
