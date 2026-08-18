/**
 * RAG search actions (RAG: TESTING).
 *
 * Calls the minimal @rag-search endpoint: single-turn RAG search,
 * question -> answer + source documents. Debug plumbing to exercise
 * the feature from the site; the real search UX lands separately.
 *
 * @module actions/ragsearch/ragsearch
 */

export const RAG_SEARCH = 'RAG_SEARCH';
export const RESET_RAG_SEARCH = 'RESET_RAG_SEARCH';

/**
 * RAG search function.
 * @function ragSearch
 * @param {string} url Url to use as base.
 * @param {string} question The natural language question.
 * @returns {Object} RAG search action.
 */
export function ragSearch(url, question, pathPrefix, extraConditions) {
  const params = [`q=${encodeURIComponent(question)}`];
  if (pathPrefix) {
    // Restrict retrieval (and thus the answer's grounding) to a
    // subtree, e.g. the current workspace.
    params.push(`path_prefix=${encodeURIComponent(pathPrefix)}`);
  }
  if (extraConditions) {
    // Encoded filter conditions (see encodeExtraConditions): the
    // answer is grounded only on documents matching the criteria.
    params.push(`extra_conditions=${encodeURIComponent(extraConditions)}`);
  }
  return {
    type: RAG_SEARCH,
    request: {
      op: 'get',
      path: `${url}/@rag-search?${params.join('&')}`,
    },
  };
}

/**
 * Reset RAG search function.
 * @function resetRagSearch
 * @returns {Object} Reset RAG search action.
 */
export function resetRagSearch() {
  return {
    type: RESET_RAG_SEARCH,
  };
}
