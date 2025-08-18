import {
  solrSearchSuggestions,
  GET_SOLR_SEARCH_SUGGESTIONS,
} from './solrSearchSuggestions';

describe('SOLR search suggestion action', () => {
  describe('solrSearchSuggestions', () => {
    it('should create an action to get the search results', () => {
      const text = 'cows';
      const action = solrSearchSuggestions(text);

      expect(action.type).toEqual(GET_SOLR_SEARCH_SUGGESTIONS);
      expect(action.request.op).toEqual('get');
      expect(action.request.path).toEqual(`/@solr-suggest?query=${text}`);
    });
  });
});
