import '@plone/volto-testing/cypress/support/commands';

const PLONE_API_URL = `http://localhost:55001/plone`;

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

// --- CREATE CONTENT (with slate blocks)--------------------------------------------------------
Cypress.Commands.add(
  'createContent',
  ({
    contentType,
    contentId,
    contentTitle,
    contentDescription,
    contentHeadTitle,
    contentText = '',
    contentSubjects,
    contentTopics,
    contentContactName,
    contentWebsite,
    contentContactMail,
    contentEffective,
    reviewState = 'published',
    withImage,
    path = '',
    allow_discussion = false,
    blocks = {
      'd3f1c443-583f-4e8e-a682-3bf25752a300': { '@type': 'title' },
      '7624cf59-05d0-4055-8f55-5fd6597d84b0': {
        '@type': 'slate',
        plaintext: contentText,
        body_text: contentText,
        value: [
          {
            children: [
              {
                text: contentText,
              },
            ],
            type: 'p',
          },
        ],
      },
    },
    blocksLayout = {
      items: [
        'd3f1c443-583f-4e8e-a682-3bf25752a300',
        '7624cf59-05d0-4055-8f55-5fd6597d84b0',
      ],
    },
    alt_tag = 'Alt text',
    target_url = '',
    language = 'en',
    ...props
  }) => {
    let api_url, auth;
    api_url = 'http://localhost:55001/plone';
    auth = {
      user: 'admin',
      pass: 'secret',
    };

    if (contentType === 'File') {
      return cy.request({
        method: 'POST',
        url: `${api_url}${path}`,
        headers: {
          Accept: 'application/json',
        },
        auth: auth,
        body: {
          '@type': contentType,
          id: contentId,
          title: contentTitle,
          description: contentDescription,
          subjects: contentSubjects,
          topic: contentTopics,
          effective: contentEffective,
          file: {
            data: 'dGVzdGZpbGUK',
            encoding: 'base64',
            filename: 'lorem.txt',
            'content-type': 'text/plain',
          },
          allow_discussion: allow_discussion,
          review_state: reviewState,
          language,
        },
      });
    }
    if (contentType === 'Image') {
      return cy.request({
        method: 'POST',
        url: `${api_url}${path}`,
        headers: {
          Accept: 'application/json',
        },
        auth: auth,
        body: {
          '@type': contentType,
          id: contentId,
          title: contentTitle,
          description: contentDescription,
          subjects: contentSubjects,
          effective: contentEffective,
          image: {
            data:
              'iVBORw0KGgoAAAANSUhEUgAAANcAAAA4CAMAAABZsZ3QAAAAM1BMVEX29fK42OU+oMvn7u9drtIPisHI4OhstdWZyt4fkcXX5+sAg74umMhNp86p0eJ7vNiKw9v/UV4wAAAAAXRSTlMAQObYZgAABBxJREFUeF7tmuty4yAMhZG4X2zn/Z92J5tsBJwWXG/i3XR6frW2Y/SBLIRAfaQUDNt8E5tLUt9BycfcKfq3R6Mlfyimtx4rzp+K3dtibXkor99zsEqLYZltblTecciogoh+TXfY1Ve4dn07rCDGG9dHSEEOg/GmXl0U1XDxTKxNK5De7BxsyyBr6gGm2/vPxKJ8F6f7BXKfRMp1xIWK9A+5ks25alSb353dWnDJN1k35EL5f8dVGifTf/4tjUuuFq7u4srmXC60yAmldLXIWbg65RKU87lcGxJCFqUPv0IacW0PmSivOZFLE908inPToMmii/roG+MRV/O8FU88i8tFsxV3a06MFUw0Qu7RmAtdV5/HVVaOVMTWNOWSwMljLhzhcB6XIS7OK5V6AvRDNN7t5VJWQs1J40UmalbK56usBG/CuCHSYuc+rkUGeMCViNRARPrzW52N3oQLe6WifNliSuuGaH3czbVNudI9s7ZLUCLHVwWlyES522o1t14uvmbblmVTKqFjaZYJFSTPP4dLL1kU1z7p0lzdbRulmEWLxoQX+z9ce7A8GqEEucllLxePuZwdJl1Lezu0hoswvTPt61DrFcRuujV/2cmlxaGBC7Aw6cpovGANwRiSdOAWJ5AGy4gLL64dl0QhUEAuEUNws+XxV+OKGPdw/hESGYF9XEGaFC7sNLMSXWJjHsnanYi87VK428N2uxpOjOFANcagLM5l+7mSycM8KknZpKLcGi6jmzWGr/vLurZ/0g4u9AZuAoeb5r1ceQhyiTPY1E4wUR6u/F3H2ojSpXMMriBPT9cezTto8Cx+MsglHL4fv1Rxrb1LVw9yvyQpJ3AhFnLZfuRLH2QsOG3FGGD20X/th/u5bFAt16Bt308KjF+MNOXgl/SquIEySX3GhaZvc67KZbDxcCDORz2N8yCWPaY5lyQZO7lQ29fnZbt3Xu6qoge4+DjXl/MocySPOp9rlvdyznahRyHEYd77v3LhugOXDv4J65QXfl803BDAdaWBEDhfVx7nKofjoVCgxnUAqw/UAUDPn788BDvQuG4TDtdtUPvzjSlXAB8DvaDOhhrmhwbywylXAm8CvaouikJTL93gs3y7Yy4VYbIxOHrcMizPqWOjqO9l3Uz52kibQy4xxOgqhJvD+w5rvokOcAlGvNCfeqCv1ste1stzLm0f71Iq3ZfTrPfuE5nhPtF+LvQE2lffQC7pYtQy3tdzdrKvd5TLVVzDetScS3nEKmmwDyt1Cev1kX3YfbvzNK4fzrlw+cB6vm+uiUgf2zdXI62241LawCb7Pi5FXFPF8KpzDoF/Sw2lg+GrHNbno1mhPu+VCF/vfMnw06PnUl6j48dVHD3jHNHPua+fc3o/5yp/zsGi0vYtzi3Pz5mHd4T6BWMIlewacd63AAAAAElFTkSuQmCC',
            encoding: 'base64',
            filename: 'image.png',
            'content-type': 'image/png',
          },
          review_state: reviewState,
          alt_tag: alt_tag,
          shows_people: false,
          language,
        },
      });
    }
    if (contentType === 'Video') {
      return cy.request({
        method: 'POST',
        url: `${api_url}${path}`,
        headers: {
          Accept: 'application/json',
        },
        auth: auth,
        body: {
          '@type': contentType,
          id: contentId,
          title: contentTitle,
          description: contentDescription,
          subjects: contentSubjects,
          effective: contentEffective,
          target_url: target_url,
          shows_people: false,
          language,
        },
      });
    }

    if (
      ['Document', 'News Item', 'Folder', 'CMSFolder'].includes(contentType)
    ) {
      if (withImage) {
        cy.createContent({
          contentType: 'Image',
          contentId: 'my-image',
          contentTitle: 'My Image',
          path: '/en',
        });
      }
      return cy
        .request({
          method: 'POST',
          url: `${api_url}${path}`,
          headers: {
            Accept: 'application/json',
          },
          auth: auth,
          // failOnStatusCode: false,
          body: {
            '@type': contentType,
            id: contentId,
            title: contentTitle,
            description: contentDescription,
            head_title: contentHeadTitle,
            subjects: contentSubjects,
            effective: contentEffective,
            blocks: blocks,
            blocks_layout: blocksLayout,
            allow_discussion: allow_discussion,
            review_state: reviewState,
            language,
            ...(withImage ? { preview_image_link: '/en/my-image' } : null),
          },
        })
        .then(() => console.log(`${contentType} created`));
    } else {
      return cy
        .request({
          method: 'POST',
          url: `${api_url}/${path}`,
          headers: {
            Accept: 'application/json',
          },
          auth: auth,
          body: {
            '@type': contentType,
            id: contentId,
            title: contentTitle,
            description: contentDescription,
            head_title: contentHeadTitle,
            subjects: contentSubjects,
            effective: contentEffective,
            allow_discussion: allow_discussion,
            review_state: reviewState,
            contact_name: contentContactName,
            event_url: contentWebsite,
            contact_email: contentContactMail,
            language,
            ...props,
          },
        })
        .then(() => console.log(`${contentType} created`));
    }
  },
);
