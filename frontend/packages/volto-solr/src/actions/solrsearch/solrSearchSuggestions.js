export const GET_SOLR_SEARCH_SUGGESTIONS = 'GET_SOLR_SEARCH_SUGGESTIONS';

/**
 * Fetch live search suggestions.
 * @param {string} term The (url-encoded) search term.
 * @param {string=} pathPrefix Optional path to restrict the suggestions
 * to a subtree (e.g. the current workspace).
 */
export function solrSearchSuggestions(term, pathPrefix) {
  const params = [`query=${term}`];
  if (pathPrefix) {
    params.push(`path_prefix=${encodeURIComponent(pathPrefix)}`);
  }
  return {
    type: GET_SOLR_SEARCH_SUGGESTIONS,
    request: {
      op: 'get',
      path: `/@solr-suggest?${params.join('&')}`,
    },
  };
}
