import '@plone/volto-testing/cypress/support/commands';

// --- AUTOLOGIN -------------------------------------------------------------
Cypress.Commands.add('autologin', (usr, pass) => {
  let api_url, user, password;
  if (Cypress.env('API') === 'guillotina') {
    api_url = GUILLOTINA_API_URL;
    user = usr || 'admin';
    password = pass || 'admin';
  } else {
    api_url = PLONE_API_URL;
    user = usr || 'admin';
    password = pass || 'secret';
  }

  return cy
    .request({
      method: 'POST',
      url: `${api_url}/@login`,
      headers: { Accept: 'application/json' },
      body: { login: user, password: password },
    })
    .then((response) => cy.setCookie('auth_token', response.body.token));
});

// --- AUTOLOGOUT ----------------------------------------------------------
Cypress.Commands.add('autologout', () => {
  let api_url, user, password;
  api_url = 'http://localhost:55001/plone';
  user = 'admin';
  password = 'secret';

  return cy
    .request({
      method: 'POST',
      url: `${api_url}/@logout`,
      headers: { Accept: 'application/json' },
      body: { login: user, password: password },
    })
    .then((response) => cy.clearCookie('auth_token'));
});

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
  const api_url = 'http://localhost:55001/plone';
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
