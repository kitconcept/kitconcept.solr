context('Search Acceptance Tests (UI)', () => {
  beforeEach(() => {
    // Docker compose setup requires host: solr-acceptance
    cy.setRegistry('collective.solr.host', 'solr-acceptance');
    cy.setRegistry('collective.solr.active', true);
    cy.setRegistry('collective.solr.use_tika', true);
    cy.reindexSolr();
    // content
    cy.createContent({
      contentType: 'Document',
      contentId: 'alpha',
      contentTitle: 'Alpha Beta Gaga Colorful',
      path: '/',
    });
    cy.request({
      method: 'POST',
      url: `http://localhost:55001/plone/alpha/@workflow/publish`,
      headers: {
        Accept: 'application/json',
      },
      auth: {
        user: 'admin',
        pass: 'secret',
      },
    });
    cy.createContent({
      contentType: 'Document',
      contentId: 'beta',
      contentTitle: 'Beta Colorful',
      path: '',
    });
    cy.request({
      method: 'POST',
      url: `http://localhost:55001/plone/beta/@workflow/publish`,
      headers: {
        Accept: 'application/json',
      },
      auth: {
        user: 'admin',
        pass: 'secret',
      },
    });
    cy.createContent({
      contentType: 'Document',
      contentId: 'gamma',
      contentTitle: 'Gamma Colorful',
      path: '',
    });
    cy.request({
      method: 'POST',
      url: `http://localhost:55001/plone/gamma/@workflow/publish`,
      headers: {
        Accept: 'application/json',
      },
      auth: {
        user: 'admin',
        pass: 'secret',
      },
    });
  });
  afterEach(() => {
    cy.clearSolr();
  });

  it('sorting', function () {
    cy.autologout();

    cy.visit('http://localhost:3000/search');
    cy.get('.searchinput').type('colorful beta');
    cy.get('.search-input button').click();

    cy.get('.total-bar .results').contains('3');

    cy.get('.tileItem .summary').should(($div) => {
      expect($div.get(0).innerText).to.eq('Beta Colorful');
      expect($div.get(1).innerText).to.eq('Alpha Beta Gaga Colorful');
      expect($div.get(2).innerText).to.eq('Gamma Colorful');
    });

    cy.get('#sort_by .react-select__control').click();
    cy.contains('Alphabetically').click();

    cy.get('.tileItem .summary').should(($div) => {
      expect($div.get(0).innerText).to.eq('Alpha Beta Gaga Colorful');
      expect($div.get(1).innerText).to.eq('Beta Colorful');
      expect($div.get(2).innerText).to.eq('Gamma Colorful');
    });

    cy.get('#sort_by .react-select__control').click();
    cy.contains('Date (newest first)').click();

    cy.get('.tileItem .summary').should(($div) => {
      expect($div.get(0).innerText).to.eq('Gamma Colorful');
      expect($div.get(1).innerText).to.eq('Beta Colorful');
      expect($div.get(2).innerText).to.eq('Alpha Beta Gaga Colorful');
    });
  });

  it('batching', function () {
    for (let i = 0; i < 50; i++) {
      cy.createContent({
        contentType: 'Document',
        contentId: `batched${i}`,
        contentTitle: `One of a bunch ${i}`,
        path: '',
      });
      cy.request({
        method: 'POST',
        url: `http://localhost:55001/plone/batched${i}/@workflow/publish`,
        headers: {
          Accept: 'application/json',
        },
        auth: {
          user: 'admin',
          pass: 'secret',
        },
      });
    }

    cy.autologout();

    cy.visit('http://localhost:3000/search');
    cy.get('.searchinput').type('bunch');
    cy.get('.search-input button').click();

    cy.get('#sort_by .react-select__control').click();
    cy.contains('Alphabetically').click();

    cy.get('.total-bar .results').contains('50');

    cy.get('.tileItem .summary').should(($div) => {
      expect($div).to.have.length(25);
      expect($div.get(0).innerText).to.eq('One of a bunch 0');
      expect($div.get(24).innerText).to.eq('One of a bunch 24');
    });

    cy.get('.search-footer').contains('2').click();

    cy.get('.tileItem .summary').should(($div) => {
      expect($div).to.have.length(25);
      expect($div.get(0).innerText).to.eq('One of a bunch 25');
      expect($div.get(24).innerText).to.eq('One of a bunch 49');
    });
  });

  it('facets', function () {
    cy.createContent({
      contentType: 'File',
      contentId: 'file1',
      contentTitle: 'Colorful beta file',
      path: '',
    });
    cy.autologout();

    cy.visit('http://localhost:3000/search');
    cy.get('.searchinput').type('colorful beta');
    cy.get('.search-input button').click();

    cy.get('.total-bar .results').contains('4');
    cy.get('.searchTab').eq(0).should('have.class', 'active');

    cy.get('.searchTab').should(($div) => {
      expect($div.get(0).innerText).to.eq('All4');
      expect($div.get(1).innerText).to.eq('Pages3');
      expect($div.get(2).innerText).to.eq('Events0');
      expect($div.get(3).innerText).to.eq('Images0');
      expect($div.get(4).innerText).to.eq('Files1');
    });

    cy.get('.searchTab .searchCounter').should(($div) => {
      expect($div.get(0).innerText).to.eq('4');
      expect($div.get(1).innerText).to.eq('3');
      expect($div.get(2).innerText).to.eq('0');
      expect($div.get(3).innerText).to.eq('0');
      expect($div.get(4).innerText).to.eq('1');
    });

    cy.get('.searchTab').eq(1).click();
    cy.get('.searchTab').eq(1).should('have.class', 'active');
    cy.get('.total-bar .results').contains('3');

    cy.get('.searchTab').eq(4).click();
    cy.get('.searchTab').eq(4).should('have.class', 'active');
    cy.get('.total-bar .results').contains('1');

    cy.get('.searchTab').eq(0).click();
    cy.get('.searchTab').eq(0).should('have.class', 'active');
    cy.get('.total-bar .results').contains('4');

    cy.get('.searchTab').eq(2).click();
    cy.get('.searchTab').eq(2).should('not.have.class', 'active');

    cy.get('.searchTab').eq(3).click();
    cy.get('.searchTab').eq(3).should('not.have.class', 'active');
  });

  /*
  it('clear search', function () {
    cy.autologout();

    cy.visit('http://localhost:3000/search');
    cy.get('.searchinput').type('colorful beta');

    cy.get('.search-input-wrapper .clear-icon').click();

    cy.get('.search-input button').click();

    cy.url().should('include', 'SearchableText=&');
    cy.get('.total-bar .results').eq('');
  });
*/
});
