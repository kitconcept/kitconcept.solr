import { solrSearchContent } from '@kitconcept/volto-solr/actions';
import {
  SolrSearch,
  SolrFormattedDate,
} from '@kitconcept/volto-solr/components';
import * as searchResultItems from '@kitconcept/volto-solr/components/theme/SolrSearch/resultItems';
import reducers from './reducers';
import routes from './routes';
import './theme/solrsearch.less';

const applyConfig = (config) => {
  config.settings.nonContentRoutes = [
    ...config.settings.nonContentRoutes,
    /.*\/@@search/,
  ];

  // --
  // View type mapping for the search results in support of Search.jsx
  // --

  // View mapper can be specified here. with the desired type rendererers.
  // The default view applies for all content types not in the array.
  // Or just use the built in mapper.
  config.views.contentTypeSearchResultViews = {
    Event: searchResultItems.EventResultItem,
    Image: searchResultItems.ImageResultItem,
  };
  config.views.contentTypeSearchResultDefaultView =
    searchResultItems.DefaultResultItem;

  // Options for solr search which can be customized
  config.settings.solrSearchOptions = config.settings.solrSearchDefaultOptions = {
    searchAction: solrSearchContent,
    getSearchReducer: (state) => state.solrsearch,
    contentTypeSearchResultViews: config.views.contentTypeSearchResultViews,
    contentTypeSearchResultDefaultView:
      config.views.contentTypeSearchResultDefaultView,
    showSearchInput: true,
  };

  // Wrapper for a customized Solr Search component that can be used
  // directly as a route.
  config.widgets.SolrSearch = SolrSearch;
  config.widgets.SolrFormattedDate = SolrFormattedDate;

  config.addonReducers = { ...config.addonReducers, ...reducers };
  config.addonRoutes = [...config.addonRoutes, ...routes(config)];

  return config;
};

export default applyConfig;
