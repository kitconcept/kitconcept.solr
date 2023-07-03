import {
  solrSearchContent,
  resetSolrSearchContent,
  copyContentForSolr,
  SOLR_SEARCH_CONTENT,
  RESET_SOLR_SEARCH_CONTENT,
  COPY_CONTENT_FOR_SOLR,
} from './solrsearch';

describe('SOLR search action', () => {
  describe('solrSearchContent', () => {
    it('should create an action to get the search results', () => {
      const text = 'cows';
      const url = '/blog';
      const action = solrSearchContent(url, { SearchableText: text });

      expect(action.type).toEqual(SOLR_SEARCH_CONTENT);
      expect(action.request.op).toEqual('get');
      expect(action.request.path).toEqual(`${url}/@solr?q=${text}&rows=25`);
    });

    describe('empty search terms', () => {
      it('if SearchableText, portal_type, review_state are all missing, no request is made and results are cleared', () => {
        const url = '/blog';
        const action = solrSearchContent(url, {});

        expect(action.type).toEqual(RESET_SOLR_SEARCH_CONTENT);
        expect(action.subrequest).toBe(null);
      });

      it('if SearchableText, portal_type, review_state are all missing, no request is made and results are cleared, with subrequest', () => {
        const url = '/blog';
        const action = solrSearchContent(url, {}, 'my-subrequest');

        expect(action.type).toEqual(RESET_SOLR_SEARCH_CONTENT);
        expect(action.subrequest).toEqual('my-subrequest');
      });

      it('if SearchableText is missing but portal_type is specified, q=* will be provided', () => {
        const url = '/blog';
        const portalType = 'Document';
        const action = solrSearchContent(url, { portal_type: portalType });

        expect(action.type).toEqual(SOLR_SEARCH_CONTENT);
        expect(action.request.op).toEqual('get');
        expect(action.request.path).toEqual(
          `${url}/@solr?portal_type=${portalType}&q=*&rows=25`,
        );
      });

      it('if SearchableText is missing but review_state is specified, q=* will be provided', () => {
        const url = '/blog';
        const reviewState = 'published';
        const action = solrSearchContent(url, { review_state: reviewState });

        expect(action.type).toEqual(SOLR_SEARCH_CONTENT);
        expect(action.request.op).toEqual('get');
        expect(action.request.path).toEqual(
          `${url}/@solr?review_state=${reviewState}&q=*&rows=25`,
        );
      });
    });

    it('can be called with an option that is an array', () => {
      const text = 'cows';
      const url = '/blog';
      const portalTypes = ['Document', 'Image'];
      const action = solrSearchContent(url, {
        SearchableText: text,
        portal_type: portalTypes,
      });

      expect(action.type).toEqual(SOLR_SEARCH_CONTENT);
      expect(action.request.op).toEqual('get');
      expect(action.request.path).toEqual(
        `${url}/@solr?portal_type:list=Document&portal_type:list=Image&q=${text}&rows=25`,
      );
    });

    it('can be called with several options that are arrays', () => {
      const text = 'cows';
      const url = '/blog';
      const portalTypes = ['Document', 'Image'];
      const workflows = ['published', 'private'];
      const action = solrSearchContent(url, {
        SearchableText: text,
        portal_type: portalTypes,
        review_state: workflows,
      });

      expect(action.type).toEqual(SOLR_SEARCH_CONTENT);
      expect(action.request.op).toEqual('get');
      expect(action.request.path).toEqual(
        `${url}/@solr?portal_type:list=Document&portal_type:list=Image&review_state:list=published&review_state:list=private&q=${text}&rows=25`,
      );
    });

    it('can be called ONLY with options that are arrays', () => {
      const url = '/blog';
      const portalTypes = ['Document', 'Image'];
      const workflows = ['published', 'private'];
      const action = solrSearchContent(url, {
        portal_type: portalTypes,
        review_state: workflows,
      });

      expect(action.type).toEqual(SOLR_SEARCH_CONTENT);
      expect(action.request.op).toEqual('get');
      expect(action.request.path).toEqual(
        `${url}/@solr?portal_type:list=Document&portal_type:list=Image&review_state:list=published&review_state:list=private&q=*&rows=25`,
      );
    });

    it('can be called without extra options', () => {
      const url = '/blog';
      const action = solrSearchContent(url);

      expect(action.type).toEqual(RESET_SOLR_SEARCH_CONTENT);
    });

    it('can be called with a subrequest key', () => {
      const url = '/blog';
      const portalType = 'Document';
      const action = solrSearchContent(
        url,
        { portal_type: portalType },
        'my-subrequest',
      );

      expect(action.type).toEqual(SOLR_SEARCH_CONTENT);
      expect(action.subrequest).toEqual('my-subrequest');
      expect(action.request.op).toEqual('get');
      expect(action.request.path).toEqual(
        `${url}/@solr?portal_type=${portalType}&q=*&rows=25`,
      );
    });

    describe('localized search', () => {
      it('local=true', () => {
        const text = 'cows';
        const url = '/blog';
        const action = solrSearchContent(url, {
          SearchableText: text,
          local: 'true',
          path_prefix: '/foo/bar',
        });
        expect(action.type).toEqual(SOLR_SEARCH_CONTENT);
        expect(action.request.op).toEqual('get');
        expect(action.request.path).toEqual(
          `${url}/@solr?q=${text}&rows=25&path_prefix=/foo/bar`,
        );
      });

      it('local=True', () => {
        const text = 'cows';
        const url = '/blog';
        const action = solrSearchContent(url, {
          SearchableText: text,
          local: 'True',
          path_prefix: '/foo/bar',
        });
        expect(action.type).toEqual(SOLR_SEARCH_CONTENT);
        expect(action.request.op).toEqual('get');
        expect(action.request.path).toEqual(
          `${url}/@solr?q=${text}&rows=25&path_prefix=/foo/bar`,
        );
      });

      it('local=false', () => {
        const text = 'cows';
        const url = '/blog';
        const action = solrSearchContent(url, {
          SearchableText: text,
          local: 'false',
          path_prefix: '/foo/bar',
        });
        expect(action.type).toEqual(SOLR_SEARCH_CONTENT);
        expect(action.request.op).toEqual('get');
        expect(action.request.path).toEqual(`${url}/@solr?q=${text}&rows=25`);
      });

      it('local missing', () => {
        const text = 'cows';
        const url = '/blog';
        const action = solrSearchContent(url, {
          SearchableText: text,
          path_prefix: '/foo/bar',
        });
        expect(action.type).toEqual(SOLR_SEARCH_CONTENT);
        expect(action.request.op).toEqual('get');
        expect(action.request.path).toEqual(`${url}/@solr?q=${text}&rows=25`);
      });

      it('local=true, path_prefix missing', () => {
        const text = 'cows';
        const url = '/blog';
        const action = solrSearchContent(url, {
          SearchableText: text,
          local: 'true',
        });
        expect(action.type).toEqual(SOLR_SEARCH_CONTENT);
        expect(action.request.op).toEqual('get');
        expect(action.request.path).toEqual(`${url}/@solr?q=${text}&rows=25`);
      });
    });
  });

  describe('resetSolrSearchContent', () => {
    it('can be called', () => {
      const action = resetSolrSearchContent();
      expect(action.type).toEqual(RESET_SOLR_SEARCH_CONTENT);
    });

    it('can be called with a subrequest', () => {
      const action = resetSolrSearchContent('my-subrequest');

      expect(action.type).toEqual(RESET_SOLR_SEARCH_CONTENT);
      expect(action.subrequest).toEqual('my-subrequest');
    });
  });

  describe('copyContentForSolr', () => {
    it('can be called', () => {
      const action = copyContentForSolr('{CONTENT}', 'QUERY');
      expect(action.content).toEqual('{CONTENT}');
      expect(action.query).toEqual('QUERY');
      expect(action.type).toEqual(COPY_CONTENT_FOR_SOLR);
      expect(action.subrequest).toBe(null);
    });

    it('can be called with a subrequest', () => {
      const action = copyContentForSolr('{CONTENT}', 'QUERY', 'my-subrequest');
      expect(action.type).toEqual(COPY_CONTENT_FOR_SOLR);
      expect(action.content).toEqual('{CONTENT}');
      expect(action.query).toEqual('QUERY');
      expect(action.subrequest).toEqual('my-subrequest');
    });
  });
});
