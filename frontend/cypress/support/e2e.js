import 'cypress-axe';
import 'cypress-file-upload';
import './commands';
import 'cypress-axe';
import { setup, teardown } from '@plone/volto/cypress/support/reset-fixture';

beforeEach(function () {
  cy.log('Setting up cookies');
  cy.setCookie('confirm_cookies', '1');
  cy.setCookie('confirm_tracking', '1');
  cy.setCookie('confirm_facebook', '1');
  cy.setCookie('confirm_youtube', '1');
  cy.log('Setting up API fixture');
  setup();
});

afterEach(function () {
  cy.log('Tearing down API fixture');
  teardown();
});
