export const GET_SOLR_SEARCH_SUGGESTIONS = 'GET_SOLR_SEARCH_SUGGESTIONS';

export function solrSearchSuggestions(term) {
  return {
    type: GET_SOLR_SEARCH_SUGGESTIONS,
    request: {
      op: 'get',
      path: `/@solr-suggest?query=${term}`,
    },
  };
}
