import { bToA } from '../../components/theme/SolrSearch/base64Helpers';

export const GET_SOLR_SEARCH_SUGGESTIONS = 'GET_SOLR_SEARCH_SUGGESTIONS';

/**
 * Encode extra conditions for the `extra_conditions` parameter, as
 * understood by both the `@solr` and the `@solr-suggest` endpoints:
 * a base64 encoded JSON list of [fieldname, kind, condition] rows,
 * e.g. [['portal_type', 'string', {in: ['News Item']}]].
 * Returns an empty string for no conditions, so the parameter can be
 * omitted with a plain falsiness check.
 * @param {Array} rows The condition rows.
 */
export function encodeExtraConditions(rows) {
  return rows && rows.length > 0 ? bToA(JSON.stringify(rows)) : '';
}

/**
 * Fetch live search suggestions.
 * @param {string} term The (url-encoded) search term.
 * @param {string=} pathPrefix Optional path to restrict the suggestions
 * to a subtree (e.g. a subsite or workspace).
 * @param {string=} extraConditions Optional encoded filter conditions
 * (see encodeExtraConditions).
 */
export function solrSearchSuggestions(term, pathPrefix, extraConditions) {
  const params = [`query=${term}`];
  if (pathPrefix) {
    params.push(`path_prefix=${encodeURIComponent(pathPrefix)}`);
  }
  if (extraConditions) {
    params.push(`extra_conditions=${encodeURIComponent(extraConditions)}`);
  }
  return {
    type: GET_SOLR_SEARCH_SUGGESTIONS,
    request: {
      op: 'get',
      path: `/@solr-suggest?${params.join('&')}`,
    },
  };
}
