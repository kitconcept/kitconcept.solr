/**
 * Routes.
 * @module routes
 */

import Search from '@plone/volto/components/theme/Search/Search';

/**
 *
 * Routes array.
 * @array
 * @returns {array} Routes.
 */

const makeConditionalSolrSearch = (config) => (props) => {
  if (config.settings.solrSearchOptions.isBackendAvailable()) {
    return config.widgets.SolrSearch({ ...config.settings.solrSearchOptions, ...props });
  } else {
    // fall back to normal Volto search if backend not installed
    return Search(props);
  }
};

const routes = (config) => {
  const SolrSearchWithOptions = makeConditionalSolrSearch(config);
  return [
    // Add your routes here
    {
      path: `/(${config.settings?.supportedLanguages.join('|')})/search`,
      component: SolrSearchWithOptions,
    },
    {
      // Use @@ prefix to discriminate from content.
      path: `/@@search`,
      component: SolrSearchWithOptions,
    },
    {
      // Use @@ prefix to discriminate from content.
      path: `/**/@@search`,
      component: SolrSearchWithOptions,
    },
    {
      path: `/search`,
      component: SolrSearchWithOptions,
    },
  ];
};

export default routes;
