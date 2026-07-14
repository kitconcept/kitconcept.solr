/**
 * RAG search reducer (RAG: TESTING).
 * @module reducers/ragsearch/ragsearch
 */

import {
  RAG_SEARCH,
  RESET_RAG_SEARCH,
} from '../../actions/ragsearch/ragsearch';

const initialState = {
  answer: null,
  sources: [],
  error: null,
  loading: false,
  loaded: false,
};

/**
 * RAG search reducer.
 * @function ragsearch
 * @param {Object} state Current state.
 * @param {Object} action Action to be handled.
 * @returns {Object} New state.
 */
export default function ragsearch(state = initialState, action = {}) {
  switch (action.type) {
    case `${RAG_SEARCH}_PENDING`:
      return {
        ...state,
        loading: true,
        loaded: false,
        error: null,
      };
    case `${RAG_SEARCH}_SUCCESS`:
      return {
        answer: action.result?.answer || null,
        sources: action.result?.sources || [],
        error: action.result?.error || null,
        loading: false,
        loaded: true,
      };
    case `${RAG_SEARCH}_FAIL`:
      return {
        ...initialState,
        error: action.error?.message || 'The RAG search request failed.',
        loaded: true,
      };
    case RESET_RAG_SEARCH:
      return initialState;
    default:
      return state;
  }
}
