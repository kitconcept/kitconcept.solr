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
export function ragSearch(url, question) {
  return {
    type: RAG_SEARCH,
    request: {
      op: 'get',
      path: `${url}/@rag-search?q=${encodeURIComponent(question)}`,
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
