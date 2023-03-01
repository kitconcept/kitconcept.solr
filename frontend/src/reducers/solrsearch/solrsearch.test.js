import search from './solrsearch';
import {
  RESET_SOLR_SEARCH_CONTENT,
  SOLR_SEARCH_CONTENT,
  COPY_CONTENT_FOR_SOLR,
} from '@kitconcept/volto-solr/actions/solrsearch/solrsearch';

describe('SOLR search reducer', () => {
  it('should return the initial state', () => {
    expect(search()).toEqual({
      error: null,
      items: [],
      groupCounts: [],
      total: 0,
      loaded: false,
      loading: false,
      batching: {},
      subrequests: {},
    });
  });

  it('should handle SOLR_SEARCH_CONTENT_PENDING', () => {
    expect(
      search(undefined, {
        type: `${SOLR_SEARCH_CONTENT}_PENDING`,
      }),
    ).toEqual({
      error: null,
      items: [],
      groupCounts: [],
      total: 0,
      loaded: false,
      loading: true,
      batching: {},
      subrequests: {},
    });
  });

  it('should handle SOLR_SEARCH_CONTENT_SUCCESS', () => {
    expect(
      search(undefined, {
        type: `${SOLR_SEARCH_CONTENT}_SUCCESS`,
        result: {
          response: {
            docs: [
              {
                Title: 'Welcome to Plone!',
                path_string: `/Plone/front-page`,
                UID: 'UID1',
              },
            ],
            numFound: 1,
          },
          highlighting: { UID1: ['<em>Blah</em>'] },
          portal_path: '/Plone',
        },
      }),
    ).toEqual({
      error: null,
      items: [
        {
          title: 'Welcome to Plone!',
          '@id': '/front-page',
          '@type': undefined,
          UID: 'UID1',
          created: undefined,
          description: undefined,
          effective: undefined,
          extras: {},
          highlighting: ['<em>Blah</em>'],
          image_field: undefined,
          review_state: undefined,
        },
      ],
      groupCounts: [],
      total: 1,
      loaded: true,
      loading: false,
      batching: {},
      subrequests: {},
    });
  });

  it('should handle SOLR_SEARCH_CONTENT_FAIL', () => {
    expect(
      search(undefined, {
        type: `${SOLR_SEARCH_CONTENT}_FAIL`,
        error: 'failed',
      }),
    ).toEqual({
      error: 'failed',
      items: [],
      groupCounts: [],
      total: 0,
      loaded: false,
      loading: false,
      batching: {},
      subrequests: {},
    });
  });

  it('should handle RESET_SOLR_SEARCH_CONTENT', () => {
    expect(
      search(undefined, {
        type: RESET_SOLR_SEARCH_CONTENT,
      }),
    ).toEqual({
      error: null,
      items: [],
      groupCounts: [],
      total: 0,
      loaded: false,
      loading: false,
      batching: {},
      subrequests: {},
    });
  });

  it('should handle subrequest SOLR_SEARCH_CONTENT_PENDING', () => {
    expect(
      search(undefined, {
        type: `${SOLR_SEARCH_CONTENT}_PENDING`,
        subrequest: 'my-subrequest',
      }),
    ).toEqual({
      error: null,
      items: [],
      groupCounts: [],
      total: 0,
      loaded: false,
      loading: false,
      batching: {},
      subrequests: {
        'my-subrequest': {
          error: null,
          items: [],
          groupCounts: [],
          total: 0,
          loaded: false,
          loading: true,
          batching: {},
        },
      },
    });
  });

  it('should handle subrequest SOLR_SEARCH_CONTENT_SUCCESS', () => {
    expect(
      search(
        {
          subrequests: {
            'my-subrequest': {
              error: null,
              items: [],
              groupCounts: [],
              total: 0,
              loaded: false,
              loading: true,
              batching: {},
            },
          },
        },
        {
          type: `${SOLR_SEARCH_CONTENT}_SUCCESS`,
          subrequest: 'my-subrequest',
          result: {
            response: {
              docs: [
                {
                  Title: 'Welcome to Plone!',
                  path_string: `/Plone/front-page`,
                  UID: 'UID1',
                },
              ],
              numFound: 1,
            },
            highlighting: { UID1: ['<em>Blah</em>'] },
            portal_path: '/Plone',
            group_counts: [1, 2, 3, 4],
          },
        },
      ),
    ).toEqual({
      subrequests: {
        'my-subrequest': {
          error: null,
          items: [
            {
              title: 'Welcome to Plone!',
              '@id': '/front-page',
              '@type': undefined,
              UID: 'UID1',
              created: undefined,
              description: undefined,
              effective: undefined,
              extras: {},
              highlighting: ['<em>Blah</em>'],
              image_field: undefined,
              review_state: undefined,
            },
          ],
          groupCounts: [1, 2, 3, 4],
          total: 1,
          loaded: true,
          loading: false,
          batching: {},
        },
      },
    });
  });

  it('should handle subrequest SOLR_SEARCH_CONTENT_FAIL', () => {
    expect(
      search(
        {
          subrequests: {
            'my-subrequest': {
              error: null,
              items: [],
              groupCounts: [],
              total: 0,
              loaded: false,
              loading: true,
              batching: {},
            },
          },
        },
        {
          type: `${SOLR_SEARCH_CONTENT}_FAIL`,
          subrequest: 'my-subrequest',
          error: 'failed',
        },
      ),
    ).toEqual({
      subrequests: {
        'my-subrequest': {
          error: 'failed',
          items: [],
          groupCounts: [],
          total: 0,
          loaded: false,
          loading: false,
          batching: {},
        },
      },
    });
  });

  it('should handle subrequest RESET_SOLR_SEARCH_CONTENT', () => {
    expect(
      search(
        {
          subrequests: {
            'my-subrequest': {
              error: null,
              items: ['random'],
              groupCounts: [],
              total: 1,
              loaded: true,
              loading: false,
              batching: {},
            },
          },
        },
        {
          type: RESET_SOLR_SEARCH_CONTENT,
          subrequest: 'my-subrequest',
        },
      ),
    ).toEqual({
      subrequests: {},
    });
  });

  describe('should handle COPY_CONTENT_FOR_SOLR', () => {
    describe('normal', () => {
      it('no subrequest', () => {
        expect(
          search(undefined, {
            type: COPY_CONTENT_FOR_SOLR,
            content: {
              '@id': '@id-en',
              language: { token: 'en' },
              '@components': {
                translations: {
                  items: [
                    { '@id': '@id-de', language: 'de' },
                    { '@id': '@id-ca', language: 'ca' },
                  ],
                  root: { en: '@root-en', de: '@root-de', ca: '@root-ca' },
                },
              },
            },
            query: '?foo=bar&bar=baz',
          }),
        ).toEqual({
          error: null,
          items: [],
          groupCounts: [],
          total: 0,
          loaded: false,
          loading: false,
          batching: {},
          subrequests: {},
          query: '?foo=bar&bar=baz',
          translations: {
            items: [
              { '@id': '@id-de', language: 'de' },
              { '@id': '@id-ca', language: 'ca' },
              { '@id': '@id-en', language: 'en' },
            ],
            root: { en: '@root-en', de: '@root-de', ca: '@root-ca' },
          },
        });
      });

      it('with subrequest', () => {
        expect(
          search(undefined, {
            type: COPY_CONTENT_FOR_SOLR,
            content: {
              '@id': '@id-en',
              language: { token: 'en' },
              '@components': {
                translations: {
                  items: [
                    { '@id': '@id-de', language: 'de' },
                    { '@id': '@id-ca', language: 'ca' },
                  ],
                  root: { en: '@root-en', de: '@root-de', ca: '@root-ca' },
                },
              },
            },
            query: '?foo=bar&bar=baz',
            subrequest: 'my-subrequest',
          }),
        ).toEqual({
          error: null,
          items: [],
          groupCounts: [],
          total: 0,
          loaded: false,
          loading: false,
          batching: {},
          subrequests: {
            'my-subrequest': {
              query: '?foo=bar&bar=baz',
              translations: {
                items: [
                  { '@id': '@id-de', language: 'de' },
                  { '@id': '@id-ca', language: 'ca' },
                  { '@id': '@id-en', language: 'en' },
                ],
                root: { en: '@root-en', de: '@root-de', ca: '@root-ca' },
              },
            },
          },
        });
      });
    });

    describe('preserves translation if content is not specified', () => {
      it('normal', () => {
        expect(
          search(
            {
              error: null,
              items: [],
              groupCounts: [],
              total: 0,
              loaded: false,
              loading: false,
              batching: {},
              subrequests: {},
              translations: {
                items: [
                  { '@id': '@id-de', language: 'de' },
                  { '@id': '@id-ca', language: 'ca' },
                  { '@id': '@id-en', language: 'en' },
                ],
                root: { en: '@root-en', de: '@root-de', ca: '@root-ca' },
              },
            },
            {
              type: COPY_CONTENT_FOR_SOLR,
              query: '?foo=bar&bar=baz',
            },
          ),
        ).toEqual({
          error: null,
          items: [],
          groupCounts: [],
          total: 0,
          loaded: false,
          loading: false,
          batching: {},
          subrequests: {},
          query: '?foo=bar&bar=baz',
          translations: {
            items: [
              { '@id': '@id-de', language: 'de' },
              { '@id': '@id-ca', language: 'ca' },
              { '@id': '@id-en', language: 'en' },
            ],
            root: { en: '@root-en', de: '@root-de', ca: '@root-ca' },
          },
        });
      });

      it('with subrequest', () => {
        expect(
          search(
            {
              error: null,
              items: [],
              groupCounts: [],
              total: 0,
              loaded: false,
              loading: false,
              batching: {},
              subrequests: {
                'other-subrequest': '{OTHER-SUB}',
                'my-subrequest': {
                  translations: {
                    items: [
                      { '@id': '@id-de', language: 'de' },
                      { '@id': '@id-ca', language: 'ca' },
                      { '@id': '@id-en', language: 'en' },
                    ],
                    root: { en: '@root-en', de: '@root-de', ca: '@root-ca' },
                  },
                },
              },
            },
            {
              type: COPY_CONTENT_FOR_SOLR,
              query: '?foo=bar&bar=baz',
              subrequest: 'my-subrequest',
            },
          ),
        ).toEqual({
          error: null,
          items: [],
          groupCounts: [],
          total: 0,
          loaded: false,
          loading: false,
          batching: {},
          subrequests: {
            'other-subrequest': '{OTHER-SUB}',
            'my-subrequest': {
              query: '?foo=bar&bar=baz',
              translations: {
                items: [
                  { '@id': '@id-de', language: 'de' },
                  { '@id': '@id-ca', language: 'ca' },
                  { '@id': '@id-en', language: 'en' },
                ],
                root: { en: '@root-en', de: '@root-de', ca: '@root-ca' },
              },
            },
          },
        });
      });
    });
  });
});
