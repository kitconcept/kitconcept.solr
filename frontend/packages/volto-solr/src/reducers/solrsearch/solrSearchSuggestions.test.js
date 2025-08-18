import searchSuggestions from './solrSearchSuggestions';
import { GET_SOLR_SEARCH_SUGGESTIONS } from '../../actions/solrsearch/solrSearchSuggestions';

describe('SOLR search suggestions reducer', () => {
  it('should return the initial state', () => {
    expect(searchSuggestions()).toEqual({
      error: null,
      items: [],
      loaded: false,
      loading: false,
    });
  });

  it('should handle GET_SOLR_SEARCH_SUGGESTIONS_PENDING', () => {
    expect(
      searchSuggestions(undefined, {
        type: `${GET_SOLR_SEARCH_SUGGESTIONS}_PENDING`,
      }),
    ).toEqual({
      error: null,
      items: [],
      loaded: false,
      loading: true,
    });
  });

  it('should handle GET_SOLR_SEARCH_SUGGESTIONS_SUCCESS', () => {
    expect(
      searchSuggestions(undefined, {
        type: `${GET_SOLR_SEARCH_SUGGESTIONS}_SUCCESS`,
        result: {
          suggestions: ['{DOC1}', '{DOC2}'],
        },
      }),
    ).toEqual({
      error: null,
      items: ['{DOC1}', '{DOC2}'],
      loaded: true,
      loading: false,
    });
  });

  it('should handle GET_SOLR_SEARCH_SUGGESTIONS_FAIL', () => {
    expect(
      searchSuggestions(undefined, {
        type: `${GET_SOLR_SEARCH_SUGGESTIONS}_FAIL`,
        error: 'failed',
      }),
    ).toEqual({
      error: 'failed',
      items: [],
      loaded: false,
      loading: false,
    });
  });
});
