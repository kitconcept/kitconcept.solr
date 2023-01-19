/**
 * Routes.
 * @module routes
 */

/**
 *
 * Routes array.
 * @array
 * @returns {array} Routes.
 */

const makeSolrSearchWithOptions = (config) => (props) =>
  config.widgets.SolrSearch({ ...config.settings.solrSearchOptions, ...props });

const routes = (config) => {
  const SolrSearchWithOptions = makeSolrSearchWithOptions(config);
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
