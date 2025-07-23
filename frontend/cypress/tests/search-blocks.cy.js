context('Search Acceptance Tests (Blocks)', () => {
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

  // Scenario: As anonymous user I can find a term in a text block
  //   Given a public document with the title 'Colorless Green Ideas'
  //     and a text block with the term 'mytextblock'
  //     and an anonymous user
  //    When I search for 'mytextblock'
  //    Then the search returns '1' results
  //     and the search results should include 'Colorless Green Ideas'
  it('Find search term in Text Block', function () {
    // GIVEN: a public document with the title 'Colorless Green Ideas'
    // and a text block with the term 'mytextblock'
    cy.createContent({
      contentType: 'Document',
      contentId: 'colorless-green-ideas',
      contentTitle: 'Colorless Green Ideas',
      path: '',
      blocks: {
        '7f6bc7e0-970e-4f28-b06e-a2b22631c6e2': {
          '@type': 'slate',
          plaintext: 'mytextblock',
          value: [
            {
              children: [
                {
                  text: 'mytextblock',
                },
              ],
              type: 'p',
            },
          ],
        },
        'cc97c959-7fdb-41ca-8edb-78653b717945': {
          '@type': 'title',
        },
      },
      blocksLayout: {
        items: [
          'cc97c959-7fdb-41ca-8edb-78653b717945',
          '7f6bc7e0-970e-4f28-b06e-a2b22631c6e2',
        ],
      },
    });
    // the setWorkflow function does not set the workflow but instead is passed a workflow transition
    // that then changes the workflow
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
    cy.get('.searchinput').type('mytextblock');
    cy.get('.search-input button').click();
    // THEN: the search returns '1' results
    cy.get('.total-bar .results').contains('1');
    // and the search results should include 'Colorless Green Ideas'
    cy.get('#content-core').contains('Colorless Green Ideas');
  });

  it('FInd search term in text block with background color ', () => {
    cy.createContent({
      contentType: 'Document',
      contentId: 'colorless-green-ideas',
      contentTitle: 'Colorless Green Ideas',
      path: '',
      blocks: {
        '36e5d4d2-7ec5-4ae5-86d9-10585e94c087': {
          '@type': 'textPillWithStyle',
          bg_color: '#ddeeff',
          plaintext: 'My block',
          useFullBackgroundContainer: true,
          value: [
            {
              children: [
                {
                  text: 'My block',
                },
              ],
              type: 'p',
            },
          ],
        },
        '762366a1-e323-43cf-9447-99e60cbef21f': {
          '@type': 'title',
        },
      },
      blocksLayout: {
        items: [
          '762366a1-e323-43cf-9447-99e60cbef21f',
          '36e5d4d2-7ec5-4ae5-86d9-10585e94c087',
        ],
      },
    });
    // the setWorkflow function does not set the workflow but instead is passed a workflow transition
    // that then changes the workflow
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
    // WHEN: I search for 'My text block with background color'
    cy.visit('http://localhost:3000/search');
    cy.get('.searchinput').type('My block');
    cy.get('.search-input button').click();
    // THEN: the search returns '1' results
    cy.get('.total-bar .results').contains('1');
    // and the search results should include 'Colorless Green Ideas'
    cy.get('#content-core').contains('Colorless Green Ideas');
  });

  it('FInd search term in introduction block ', () => {
    cy.createContent({
      contentType: 'Document',
      contentId: 'colorless-green-ideas',
      contentTitle: 'Colorless Green Ideas',
      path: '',
      blocks: {
        '0994b803-483f-4799-b868-1b9f62d4b8cc': {
          '@type': 'introduction',
          about: {
            0: {
              children: [
                {
                  text: '',
                },
              ],
              type: 'p',
            },
            value: [
              {
                children: [
                  {
                    text: 'Introduction Blocks Thisis me',
                  },
                ],
                type: 'p',
              },
            ],
          },
          academic: '',
          building: '',
          email: '',
          firstname: '',
          heading: 'Introduction Block',
          image: '',
          institute: '',
          mobile: '',
          name: '',
          phone: '',
          positions: '',
          room: '',
          salutation: '',
          topics: {
            0: {
              children: [
                {
                  text: '',
                },
              ],
              type: 'p',
            },
            value: [
              {
                children: [
                  {
                    text: 'Introduction Block Topics',
                  },
                ],
                type: 'p',
              },
            ],
          },
        },
        '56da4220-d429-4409-b6a4-2ab10145ac5f': {
          '@type': 'slate',
          plaintext: '',
          value: [
            {
              children: [
                {
                  text: '',
                },
              ],
              type: 'p',
            },
          ],
        },
        'de772e4a-cda4-4d0f-88f6-135a802f08e0': {
          '@type': 'title',
        },
      },
      blocksLayout: {
        items: [
          'de772e4a-cda4-4d0f-88f6-135a802f08e0',
          '0994b803-483f-4799-b868-1b9f62d4b8cc',
          '56da4220-d429-4409-b6a4-2ab10145ac5f',
        ],
      },
    });
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
    // WHEN: I search for 'Introduction Block'
    cy.visit('http://localhost:3000/search');
    cy.get('.searchinput').type('Introduction Block');
    cy.get('.search-input button').click();
    // THEN: the search returns '1' results
    cy.get('.total-bar .results').contains('1');
    // and the search results should include 'Colorless Green Ideas'
    cy.get('#content-core').contains('Colorless Green Ideas');

    //also check if we can find the 'topics' and 'thisis me' fields which are part of the block
    cy.visit('http://localhost:3000/search');
    cy.get('.searchinput').type('Introduction Block Topics');
    cy.get('.search-input button').click();
    // THEN: the search returns '1' results
    cy.get('.total-bar .results').contains('1');
    // and the search results should include 'Colorless Green Ideas'
    cy.get('#content-core').contains('Colorless Green Ideas');

    cy.visit('http://localhost:3000/search');
    cy.get('.searchinput').type('Introduction Block Thisis me');
    cy.get('.search-input button').click();
    // THEN: the search returns '1' results
    cy.get('.total-bar .results').contains('1');
    // and the search results should include 'Colorless Green Ideas'
    cy.get('#content-core').contains('Colorless Green Ideas');
  });

  it('FInd search term in table block ', () => {
    cy.createContent({
      contentType: 'Document',
      contentId: 'colorless-green-ideas',
      contentTitle: 'Colorless Green Ideas',
      path: '',
      blocks: {
        '67a31986-383d-49c4-9e17-e2977de122d2': {
          '@type': 'slateTable',
          table: {
            basic: false,
            celled: true,
            compact: false,
            fixed: true,
            inverted: false,
            rows: [
              {
                cells: [
                  {
                    key: '6llm2',
                    type: 'header',
                    value: [
                      {
                        children: [
                          {
                            text: 'texxt inn column 1 row 1',
                          },
                        ],
                        type: 'p',
                      },
                    ],
                  },
                  {
                    key: '2qlt4',
                    type: 'header',
                    value: [
                      {
                        children: [
                          {
                            text: 'texxt inn column 2 row 1',
                          },
                        ],
                        type: 'p',
                      },
                    ],
                  },
                ],
                key: '1h7ev',
              },
              {
                cells: [
                  {
                    key: 'dgkm2',
                    type: 'data',
                    value: [
                      {
                        children: [
                          {
                            text: 'texxt inn column 1 row 2',
                          },
                        ],
                        type: 'p',
                      },
                    ],
                  },
                  {
                    key: '329lm',
                    type: 'data',
                    value: [
                      {
                        children: [
                          {
                            text: 'texxt inn column 2 row 2',
                          },
                        ],
                        type: 'p',
                      },
                    ],
                  },
                ],
                key: 'bbl8h',
              },
            ],
            striped: false,
          },
        },
        '762366a1-e323-43cf-9447-99e60cbef21f': {
          '@type': 'title',
        },
      },
      blocksLayout: {
        items: [
          '762366a1-e323-43cf-9447-99e60cbef21f',
          '67a31986-383d-49c4-9e17-e2977de122d2',
        ],
      },
    });
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
    // WHEN: I search for 'text in column 2 row 2'
    cy.visit('http://localhost:3000/search');
    cy.get('.searchinput').type('texxt inn column 2 row 2');
    cy.get('.search-input button').click();
    // THEN: the search returns '1' results
    cy.get('.total-bar .results').contains('1');
    // and the search results should include 'Colorless Green Ideas'
    cy.get('#content-core').contains('Colorless Green Ideas');
  });

  it('Find search term in headline block ', () => {
    cy.createContent({
      contentType: 'Document',
      contentId: 'colorless-green-ideas',
      contentTitle: 'Colorless Green Ideas',
      path: '',
      blocks: {
        '45ee8ea9-1573-46f4-9ad5-f220bfab60ae': {
          '@type': 'headline',
          bg_color: null,
          title: 'Headline Block',
        },
        '762366a1-e323-43cf-9447-99e60cbef21f': {
          '@type': 'title',
        },
      },
      blocksLayout: {
        items: [
          '762366a1-e323-43cf-9447-99e60cbef21f',
          '45ee8ea9-1573-46f4-9ad5-f220bfab60ae',
        ],
      },
    });
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
    // WHEN: I search for 'Headline Block'
    cy.visit('http://localhost:3000/search');
    cy.get('.searchinput').type('Headline Block');
    cy.get('.search-input button').click();
    // THEN: the search returns '1' results
    cy.get('.total-bar .results').contains('1');
    // and the search results should include 'Colorless Green Ideas'
    cy.get('#content-core').contains('Colorless Green Ideas');
  });
});
