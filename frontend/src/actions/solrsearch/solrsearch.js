import {
  compact,
  concat,
  isArray,
  join,
  map,
  pickBy,
  toPairs,
  identity,
} from 'lodash';
import config from '@plone/volto/registry';

export const SOLR_SEARCH_CONTENT = 'SOLR_SEARCH_CONTENT';
export const RESET_SOLR_SEARCH_CONTENT = 'RESET_SOLR_SEARCH_CONTENT';

/**
 * Search content function.
 * @function solrSearchContent
 * @param {string} url Url to use as base.
 * @param {Object} options Search options.
 * @param {string} subrequest Key of the subrequest.
 * @returns {Object} Search content action.
 */
export function solrSearchContent(url, options, subrequest = null) {
  let queryArray = [];
  options = pickBy(options, identity);
  const { settings } = config;

  const arrayOptions = pickBy(options, (item) => isArray(item));

  // XXX Note: The `portal_type` and `review_state` terms are
  // currently ignored by the `@@solr` backend service. However
  // their implementation on the front-end is ready.

  const pathPrefix =
    (options.local || '').toLowerCase() === 'true' && options.path_prefix;

  const emptySearchCondition =
    !options.SearchableText &&
    !options['portal_type'] &&
    !options['review_state'];

  if (emptySearchCondition) {
    // If none of the conditions are specified, we don't do a server
    // search but return an empty result set in a shortcut.
    // Note that an empty `q` parameter would fail anyway.
    return resetSolrSearchContent(subrequest);
  }

  queryArray = concat(
    queryArray,
    options
      ? join(
          map(toPairs(pickBy(options, (item) => !isArray(item))), (item) => {
            if (item[0] === 'b_start') {
              // Solr service uses start
              item[0] = 'start';
            } else if (
              [
                'b_size',
                'sort_on',
                'sort_order',
                'SearchableText',
                'local',
                'path_prefix',
              ].includes(item[0])
            ) {
              // Injected later
              return;
            }
            // Urlencoding needed
            const [k, v] = item;
            return `${k}=${encodeURIComponent(v)}`;
          }).filter((e) => e),
          '&',
        )
      : '',
    arrayOptions
      ? join(
          map(pickBy(arrayOptions), (item, key) => {
            if (key === 'metadata_fields') {
              // Solr service does not support it
              return '';
            } else {
              return join(
                item.map((value) => `${key}:list=${value}`),
                '&',
              );
            }
          }),
          '&',
        )
      : '',
    // SearchableText is inserted in all cases, if missing * will be applied
    `q=${options.SearchableText !== undefined ? options.SearchableText : '*'}`,
    // Default batch size is injected here
    `rows=${
      options.b_size !== undefined ? options.b_size : settings.defaultPageSize
    }`,
    pathPrefix ? `path_prefix=${options.path_prefix}` : '',
    options.sort_on !== undefined
      ? 'sort=' +
          encodeURIComponent(
            `${options.sort_on} ${
              options.sort_order === 'reverse' ? 'desc' : 'asc'
            }`,
          )
      : '',
  );

  const querystring = join(compact(queryArray), '&');

  return {
    type: SOLR_SEARCH_CONTENT,
    subrequest,
    request: {
      op: 'get',
      path: `${url}/@solr${querystring ? `?${querystring}` : ''}`,
    },
  };
}

/**
 * Reset search content function.
 * @function resetSolrSearchContent
 * @param {string} subrequest Key of the subrequest.
 * @returns {Object} Search content action.
 */
export function resetSolrSearchContent(subrequest = null) {
  return {
    type: RESET_SOLR_SEARCH_CONTENT,
    subrequest,
  };
}
