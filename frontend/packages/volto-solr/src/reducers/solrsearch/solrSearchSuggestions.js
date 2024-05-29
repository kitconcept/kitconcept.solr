import { GET_SOLR_SEARCH_SUGGESTIONS } from '../../actions/solrsearch/solrSearchSuggestions';

const initialState = {
  error: null,
  items: [],
  loaded: false,
  loading: false,
};

export default function searchSuggestions(state = initialState, action = {}) {
  switch (action.type) {
    case `${GET_SOLR_SEARCH_SUGGESTIONS}_PENDING`:
      return {
        ...state,
        error: null,
        loaded: false,
        loading: true,
      };
    case `${GET_SOLR_SEARCH_SUGGESTIONS}_SUCCESS`:
      return {
        ...state,
        error: null,
        items: action.result.suggestions,
        loaded: true,
        loading: false,
      };
    case `${GET_SOLR_SEARCH_SUGGESTIONS}_FAIL`:
      return {
        ...state,
        error: action.error,
        items: [],
        loaded: false,
        loading: false,
      };
    default:
      return state;
  }
}
