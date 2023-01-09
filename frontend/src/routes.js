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

const routes = (config) => [
  // Add your routes here
  {
    path: `/(${config.settings?.supportedLanguages.join('|')})/search`,
    component: config.widgets.SolrSearch,
  },
  {
    // Use @@ prefix to discriminate from content.
    path: `/@@search`,
    component: config.widgets.SolrSearch,
  },
  {
    // Use @@ prefix to discriminate from content.
    path: `/**/@@search`,
    component: config.widgets.SolrSearch,
  },
  {
    path: `/search`,
    component: config.widgets.SolrSearch,
  },
];

export default routes;
