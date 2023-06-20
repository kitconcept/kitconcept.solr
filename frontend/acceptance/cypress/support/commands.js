import '@plone/volto-testing/cypress/support/commands';

// --- SOLR --------------------------------------------------------------------
Cypress.Commands.add('reindexSolr', () => {
  const log = Cypress.log({
    name: 'log',
    displayName: `reindexSolr`,
  });
  const api_url = 'http://localhost:55001/plone';
  const auth = {
    user: 'admin',
    pass: 'secret',
  };
  return cy
    .request({
      method: 'GET',
      url: `${api_url}/@@solr-maintenance/reindex`,
      auth: auth,
    })
    .then(() => log.set('message', 'solr reindex complete'));
});
Cypress.Commands.add('clearSolr', () => {
  const log = Cypress.log({
    name: 'log',
    displayName: `clearSolr`,
  });
  const api_url = 'http://localhost:55001/plone';
  const auth = {
    user: 'admin',
    pass: 'secret',
  };
  return cy
    .request({
      method: 'GET',
      url: `${api_url}/@@solr-maintenance/clear`,
      auth: auth,
    })
    .then(() => log.set('message', 'solr clear complete'));
});
Cypress.Commands.add('createPDF', () => {
  const log = Cypress.log({
    name: 'log',
    displayName: `createPDF`,
  });
  const api_url = 'http://localhost:55001/plone/en';
  const auth = {
    user: 'admin',
    pass: 'secret',
  };
  cy.fixture('file.pdf', 'base64')
    .then((fc) => {
      return fc;
    })
    .then((fileContent) => {
      return cy
        .request({
          method: 'POST',
          url: `${api_url}`,
          headers: {
            Accept: 'application/json',
          },
          auth,
          body: {
            '@type': 'File',
            id: 'chomsky.pdf',
            title: 'chomsky.pdf',
            file: {
              data: fileContent,
              encoding: 'base64',
              filename: 'chomsky.pdf',
              'content-type': 'application/pdf',
            },
          },
        })
        .then(() => log.set('message', 'PDF created'));
    });
});
