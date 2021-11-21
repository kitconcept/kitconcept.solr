.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

==============================================================================
kitconcept.solr
==============================================================================

.. image:: https://kitconcept.com/logo.svg
   :alt: kitconcept
   :target: https://kitconcept.com/

.. image:: https://secure.travis-ci.org/kitconcept/kitconcept.solr/actions/workflows/ci.yml/badge.svg
   :target: https://github.com/kitconcept/kitconcept.solr/actions/workflows/ci.yml


Development
-----------

Requirements:

- Python 3.8

Setup::

  make

Run Static Code Analysis::

  make code-Analysis

Run Unit / Integration Tests::

  make test

Run Robot Framework based acceptance tests::

  make test-acceptance
