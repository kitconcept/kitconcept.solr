/**
 * SOLR Search reducer.
 * @module reducers/solrsearch/search
 */

import { map, omit } from 'lodash';
import {
  RESET_SOLR_SEARCH_CONTENT,
  SOLR_SEARCH_CONTENT,
  COPY_CONTENT_FOR_SOLR,
} from '@kitconcept/volto-solr/actions/solrsearch/solrsearch';

const initialState = {
  error: null,
  items: [],
  groupCounts: [],
  total: 0,
  loaded: false,
  loading: false,
  batching: {},
  subrequests: {},
};

const solrPathToPortalPath = (portal_path, path) => {
  if (path.startsWith(portal_path)) {
    path = path.substr(portal_path.length);
  } else {
    // eslint-disable-next-line
    console.warn(`solrsearch path with invalid prefix "${path}"`);
  }
  return path;
};

const getHighlighting = (highlighting, UID) =>
  [].concat(...(Object.values(highlighting[UID]) || {}));

const mapSolrItem = (portal_path, highlighting, item) => {
  const {
    path_string,
    Type,
    Title,
    Description,
    UID,
    created,
    effective,
    image_field,
    review_state,
    ...extras
  } = item;
  return {
    '@id': solrPathToPortalPath(portal_path, path_string),
    '@type': Type,
    title: Title,
    description: Description, // unused
    created,
    effective,
    UID, // unused
    image_field, // missing
    review_state, // missing
    highlighting: getHighlighting(highlighting, UID),
    extras,
  };
};

const getBatching = (action) => {
  // Add this eventually (not sure if it matters)
  return {};
};

const getTranslations = (content) => {
  const translations = content?.['@components']?.translations;
  // The current language translation must be added to the
  // translation array, this allows that we can use this data
  // to switch back to the original language, without the need
  // to reload the content each time the translation is changed.
  return {
    items: (translations?.items || []).concat(
      content
        ? { '@id': content['@id'], language: content.language.token }
        : [],
    ),
    root: translations?.root,
  };
};

/**
 * SOLR Search reducer.
 * @function search
 * @param {Object} state Current state.
 * @param {Object} action Action to be handled.
 * @returns {Object} New state.
 */
export default function search(state = initialState, action = {}) {
  switch (action.type) {
    case `${SOLR_SEARCH_CONTENT}_PENDING`:
      return action.subrequest
        ? {
            ...state,
            subrequests: {
              ...state.subrequests,
              [action.subrequest]: {
                ...(state.subrequests[action.subrequest] || {
                  items: [],
                  total: 0,
                  groupCounts: [],
                  batching: {},
                }),
                error: null,
                loaded: false,
                loading: true,
              },
            },
          }
        : {
            ...state,
            error: null,
            loading: true,
            loaded: false,
          };
    case `${SOLR_SEARCH_CONTENT}_SUCCESS`:
      const update = {
        error: null,
        items: map(
          action.result.response.docs,
          mapSolrItem.bind(
            null,
            action.result.portal_path,
            action.result.highlighting,
          ),
        ),
        total: action.result.response.numFound,
        groupCounts: action.result.group_counts || [],
        loaded: true,
        loading: false,
        batching: getBatching(action),
      };
      return action.subrequest
        ? {
            ...state,
            subrequests: {
              ...state.subrequests,
              [action.subrequest]: update,
            },
          }
        : {
            ...state,
            ...update,
          };
    case `${SOLR_SEARCH_CONTENT}_FAIL`:
      const updateFail = {
        error: action.error,
        items: [],
        total: 0,
        groupCounts: [],
        loading: false,
        loaded: false,
        batching: {},
      };
      return action.subrequest
        ? {
            ...state,
            subrequests: {
              ...state.subrequests,
              [action.subrequest]: updateFail,
            },
          }
        : {
            ...state,
            ...updateFail,
          };
    case RESET_SOLR_SEARCH_CONTENT:
      return action.subrequest
        ? {
            ...state,
            subrequests: omit(state.subrequests, [action.subrequest]),
          }
        : {
            ...state,
            error: null,
            items: [],
            total: 0,
            groupCounts: [],
            loading: false,
            loaded: false,
            batching: {},
          };
    case COPY_CONTENT_FOR_SOLR:
      const translationsIfSpecified = action.content
        ? { translations: getTranslations(action.content) }
        : undefined;
      return action.subrequest
        ? {
            ...state,
            subrequests: {
              ...state.subrequests,
              [action.subrequest]: {
                ...state.subrequests[action.subrequest],
                ...translationsIfSpecified,
                query: action.query,
              },
            },
          }
        : {
            ...state,
            ...translationsIfSpecified,
            query: action.query,
          };
    default:
      return state;
  }
}
