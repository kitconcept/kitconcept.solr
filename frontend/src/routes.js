/**
 * Routes.
 * @module routes
 */

import Search from '@plone/volto/components/theme/Search/Search';
import { useSelector } from 'react-redux';

/**
 *
 * Routes array.
 * @array
 * @returns {array} Routes.
 */

const makeConditionalSolrSearch = (config) => (props) => {
  const state = useSelector((state) => state);
  if (config.settings.solrSearchOptions.isBackendAvailable(state)) {
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
