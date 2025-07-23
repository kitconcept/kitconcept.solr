import { queryStateFromParams, queryStateToParams } from './SearchQuery';
import { bToA } from './base64Helpers';

// polyfill needed because of jsDom version used by jest
import { TextEncoder, TextDecoder } from 'util';
Object.assign(global, { TextDecoder, TextEncoder });

describe('SOLR SearchQuery', () => {
  describe('queryStateFromParams', () => {
    beforeEach(() => {
      jest.spyOn(console, 'warn').mockImplementation(jest.fn());
    });
    afterEach(() => {
      // eslint-disable-next-line no-console
      console.warn.mockRestore();
    });
    it('works', () => {
      expect(
        queryStateFromParams({
          allow_local: 'true',
          facet_conditions: bToA('{"foo":{"m":true}}'),
          group_select: '2',
          local: 'true',
          SearchableText: 'foobar',
          sort_on: 'alphabetic',
          sort_order: 'reverse',
        }),
      ).toEqual({
        allowLocal: true,
        facetConditions: { foo: { m: true } },
        groupSelect: 2,
        local: true,
        searchword: 'foobar',
        sortOn: 'alphabetic',
        sortOrder: 'reverse',
      });
    });
    it('initial', () => {
      expect(queryStateFromParams({})).toEqual({
        allowLocal: false,
        facetConditions: {},
        groupSelect: 0,
        local: false,
        searchword: '',
        sortOn: 'relevance',
        sortOrder: '',
      });
    });
  });
  describe('queryStateToParams', () => {
    it('works', () => {
      expect(
        queryStateToParams({
          allowLocal: true,
          facetConditions: { foo: { m: true } },
          groupSelect: 2,
          local: true,
          searchword: 'foobar',
          sortOn: 'alphabetic',
          sortOrder: 'reverse',
        }),
      ).toEqual({
        allow_local: 'true',
        facet_conditions: bToA('{"foo":{"m":true}}'),
        group_select: '2',
        local: 'true',
        SearchableText: 'foobar',
        sort_on: 'alphabetic',
        sort_order: 'reverse',
      });
    });
    it('defaults ', () => {
      expect(
        queryStateToParams({
          allowLocal: false,
          facetConditions: {},
          groupSelect: 0,
          local: false,
          searchword: '',
          sortOn: 'relevance',
          sortOrder: '',
        }),
      ).toEqual({
        allow_local: 'false',
        facet_conditions: '',
        group_select: '0',
        local: 'false',
        SearchableText: '',
        sort_on: 'relevance',
        sort_order: '',
      });
    });
    it('prunes condition tree', () => {
      expect(
        queryStateToParams({
          allowLocal: true,
          facetConditions: { foo: { p: 'prefix', m: false }, bar: {} },
          groupSelect: 2,
          local: true,
          searchword: 'foobar',
          sortOn: 'alphabetic',
          sortOrder: 'reverse',
        }),
      ).toEqual({
        allow_local: 'true',
        facet_conditions: bToA('{"foo":{"p":"prefix"}}'),
        group_select: '2',
        local: 'true',
        SearchableText: 'foobar',
        sort_on: 'alphabetic',
        sort_order: 'reverse',
      });
    });
  });
});
