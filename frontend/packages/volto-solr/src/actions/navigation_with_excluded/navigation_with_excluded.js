/**
 * Navigation with excluded items actions.
 * @module actions/navigation/navigation_with_excluded
 */

export const GET_NAVIGATION_WITH_EXCLUDED = 'GET_NAVIGATION_WITH_EXCLUDED';

/**
 * Get navigation.
 * @function getNavigationWithExcluded
 * @param {string} url Content url.
 * @param {number} depth Depth of the navigation tree.
 * @returns {Object} Get navigation action.
 */
export function getNavigationWithExcluded(url, depth) {
  // Note: Depth can't be 0 in plone.restapi
  return {
    type: GET_NAVIGATION_WITH_EXCLUDED,
    request: {
      op: 'get',
      path: `${url}/@navigation_with_excluded${
        depth ? `?expand.navigation_with_excluded.depth=${depth}` : ''
      }`,
    },
  };
}
