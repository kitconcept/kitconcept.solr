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
export const COPY_CONTENT_FOR_SOLR = 'COPY_CONTENT_FOR_SOLR';

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

  // XXX Note: The `review_state` term is
  // currently ignored by the `@@solr` backend service. However
  // its implementation on the front-end is ready.

  const pathPrefix =
    (options.local || '').toLowerCase() === 'true' && options.path_prefix;

  const emptySearchCondition =
    !options.SearchableText &&
    !options['portal_type'] &&
    !options['review_state'];

  if (!options.doEmptySearch && emptySearchCondition) {
    // If none of the conditions are specified, we don't do a server
    // search but return an empty result set in a shortcut.
    // Note that an empty `q` parameter would fail anyway.
    // This behavior is configurable by the `doEmptySearch` option.
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
    `q=${options.SearchableText ?? ''}`,
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

/**
 * Copy content for Solr.
 *
 * This copies the history (optionally) and the query string that can
 * be used switching the languages in the search page in a way that
 * both the localization and the translations work, even after the actual
 * content gets resetted.
 *
 * @function copyContentForSolr
 * @param {Object} content The original content as in `state.content.data`.
 * @param {string} query The query string of the search.
 * @param {string} subrequest Key of the subrequest.
 * @returns {Object} Search content action.
 */
export function copyContentForSolr(content, query, subrequest = null) {
  return {
    type: COPY_CONTENT_FOR_SOLR,
    content,
    query,
    subrequest,
  };
}
