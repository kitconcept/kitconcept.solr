/**
 * Search component.
 * @module components/theme/Search/Search
 */

import React, { Component, createElement, createRef, forwardRef } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { compose } from 'redux';
import { asyncConnect } from '@plone/volto/helpers';
import { FormattedMessage } from 'react-intl';
import { Portal } from 'react-portal';
import {
  Container,
  Segment,
  Pagination,
  Button,
  Dimmer,
  Loader,
  Checkbox,
} from 'semantic-ui-react';
import { injectIntl, useIntl, defineMessages } from 'react-intl';
import qs from 'query-string';

import config from '@plone/volto/registry';
import { Helmet } from '@plone/volto/helpers';
import { Toolbar, Icon } from '@plone/volto/components';

import paginationLeftSVG from '@plone/volto/icons/left-key.svg';
import paginationRightSVG from '@plone/volto/icons/right-key.svg';
// These imports and the legacySearchProps are only for the legacy search
import { searchContent } from '@plone/volto/actions';
import { DefaultResultItem } from './resultItems';
import { SelectSorting } from './SelectSorting';
import { SearchResultInfo } from './SearchResultInfo';
import { SearchTabs } from './SearchTabs';

const messages = defineMessages({
  TypeSearchWords: {
    id: 'Search...',
    defaultMessage: 'Search...',
  },
  results: {
    // Ergebnisse
    id: 'results',
    defaultMessage: 'results',
  },
  searchLocalizedLabel: {
    // Suchergebnisse anzeigen für:
    id: 'searchLocalizedLabel',
    defaultMessage: 'Show results for:',
  },
  searchGlobalized: {
    // Alle webauftritte (global)
    id: 'searchGlobalized',
    defaultMessage: 'All content (global)',
  },
  searchLocalized: {
    // Nur dieser webauftritt
    id: 'searchLocalized',
    defaultMessage: 'This subfolder only',
  },
});

// XXX for some reason formatMessage is missing from this.props.intl.
// Until we figure this out, just acquire it directly from hook.
// This should not be necessary.. @reebalazs
const TranslatedInput = forwardRef(
  ({ forwardRef, placeholder, className, value, onChange }, ref) => {
    const intl = useIntl();
    return (
      <input
        ref={ref}
        placeholder={intl.formatMessage(placeholder)}
        className={className}
        value={value}
        onChange={onChange}
      />
    );
  },
);

// Return the path prefix, or undefined, if we are on the root.
// We consider `/` and the language specific root folders `/en`, `/de` as roots
const getPathPrefix = (location) => {
  const pathPrefix = location.pathname.replace(/\/[^/]*$/, '') + '/';
  return pathPrefix.match(/^\/([^/]+\/)?$/) ? undefined : pathPrefix;
};

// XXX for some reason formatMessage is missing from this.props.intl.
// Until we figure this out, just acquire it directly from hook.
// This should not be necessary.. @reebalazs
const LocalCheckbox = ({ onChange, checked }) => {
  const intl = useIntl();
  return (
    <div className="search-localized">
      {intl.formatMessage(messages.searchLocalizedLabel)}
      <Checkbox
        radio
        label={intl.formatMessage(messages.searchGlobalized)}
        onChange={(e, data) => onChange(!data.checked)}
        checked={!checked}
      />
      <Checkbox
        radio
        label={intl.formatMessage(messages.searchLocalized)}
        onChange={(e, data) => onChange(data.checked)}
        checked={checked}
      />
    </div>
  );
};

/**
 * SolrSearch class.
 * @class SearchComponent
 * @extends Component
 */
class SolrSearch extends Component {
  /**
   * Property types.
   * @property {Object} propTypes Property types.
   * @static
   */
  static propTypes = {
    searchContent: PropTypes.func.isRequired,
    searchAction: PropTypes.func,
    getSearchReducer: PropTypes.func,
    showSearchInput: PropTypes.bool,
    contentTypeSearchResultViews: PropTypes.object,
    contentTypeSearchResultDefaultView: PropTypes.func,
    searchableText: PropTypes.string,
    subject: PropTypes.string,
    path: PropTypes.string,
    items: PropTypes.arrayOf(
      PropTypes.shape({
        '@id': PropTypes.string,
        '@type': PropTypes.string,
        title: PropTypes.string,
        description: PropTypes.string,
      }),
    ),
    loaded: PropTypes.bool,
    loading: PropTypes.bool,
    total: PropTypes.number,
    batching: PropTypes.shape({
      '@id': PropTypes.string,
      first: PropTypes.string,
      last: PropTypes.string,
      prev: PropTypes.string,
      next: PropTypes.string,
    }),
    pathname: PropTypes.string.isRequired,
  };

  /**
   * Default properties.
   * @property {Object} defaultProps Default properties.
   * @static
   */
  static defaultProps = {
    items: [],
    loaded: false,
    loading: false,
    total: 0,
    batching: null,
    searchableText: null,
    subject: null,
    path: null,
  };

  constructor(props) {
    super(props);
    this.state = {
      currentPage: 1,
      isClient: false,
      active: 'relevance',
      searchword: '',
      groupSelect: 0,
      allowLocal: false,
      local: false,
    };
    this.inputRef = createRef();
  }

  /**
   * Component did mount
   * @method componentDidMount
   * @returns {undefined}
   */
  componentDidMount() {
    this.doSearch();
    const location = this.props.history.location;
    const qoptions = qs.parse(location.search);
    this.setState({
      isClient: true,
      searchword: this.props.searchableText || '',
      active: qoptions.sort_on || 'relevance',
      groupSelect: parseInt(qoptions.group_select) || 0,
      allowLocal: (qoptions.allow_local || '').toLowerCase() === 'true',
      local: (qoptions.local || '').toLowerCase() === 'true',
    });
    // put focus to the search input field
    if (this.props.showSearchInput) {
      this.inputRef.current.focus();
    }
  }

  /**
   * Component will receive props
   * @method componentWillReceiveProps
   * @param {Object} nextProps Next properties
   * @returns {undefined}
   */
  UNSAFE_componentWillReceiveProps = (nextProps) => {
    if (this.props.location.search !== nextProps.location.search) {
      this.doSearch();
    }
  };

  /**
   * Search based on the given searchableText, subject and path.
   * @method doSearch
   * @param {string} searchableText The searchable text string
   * @param {string} subject The subject (tag)
   * @param {string} path The path to restrict the search to
   * @returns {undefined}
   */

  doSearch = () => {
    const location = this.props.history.location;
    const qoptions = qs.parse(location.search);
    this.setState({ currentPage: 1 });
    const options = {
      ...qoptions,
      path_prefix: getPathPrefix(location),
      use_site_search_settings: 1,
      metadata_fields: ['effective', 'UID', 'start'],
      hl: 'true',
    };
    this.props.searchContent('', options);
  };

  handleQueryPaginationChange = (e, { activePage }) => {
    const { settings } = config;
    window.scrollTo(0, 0);
    const qoptions = qs.parse(this.props.history.location.search);
    const options = {
      ...qoptions,
      use_site_search_settings: 1,
      metadata_fields: ['effective', 'UID', 'start'],
      hl: 'true',
    };

    this.setState({ currentPage: activePage }, () => {
      this.props.searchContent('', {
        ...options,
        b_start: (this.state.currentPage - 1) * settings.defaultPageSize,
      });
    });
  };

  onSortChange = (selectedOption, sort_order) => {
    const qoptions = qs.parse(this.props.history.location.search);
    const options = {
      ...qoptions,
      use_site_search_settings: 1,
      metadata_fields: ['effective', 'UID', 'start'],
      hl: 'true',
    };
    options.sort_on = selectedOption;
    options.sort_order = sort_order || 'ascending';
    if (selectedOption === 'relevance') {
      delete options.sort_on;
      delete options.sort_order;
    }
    let searchParams = qs.stringify(options);
    this.setState({ currentPage: 1, active: selectedOption }, () => {
      // eslint-disable-next-line no-restricted-globals
      this.props.history.replace({
        search: searchParams,
      });
    });
  };

  setGroupSelect = (groupSelect) => {
    const qoptions = qs.parse(this.props.history.location.search);
    const options = {
      ...qoptions,
      group_select: groupSelect,
    };
    let searchParams = qs.stringify(options);
    this.setState({ currentPage: 1, groupSelect }, () => {
      // eslint-disable-next-line no-restricted-globals
      this.props.history.replace({
        search: searchParams,
      });
    });
  };

  setLocal = (local) => {
    const qoptions = qs.parse(this.props.history.location.search);
    const options = {
      ...qoptions,
      local: local,
    };
    let searchParams = qs.stringify(options);
    this.setState({ currentPage: 1, local }, () => {
      // eslint-disable-next-line no-restricted-globals
      this.props.history.replace({
        search: searchParams,
      });
    });
  };

  onSubmit = (event) => {
    this.props.history.push({
      pathname: this.props.pathname,
      search: qs.stringify({
        SearchableText: this.state.searchword,
        active: this.state.active,
        group_select: this.state.groupSelect,
        allow_local: this.state.allowLocal || undefined,
        local: this.state.local,
      }),
    });
    event.preventDefault();
  };

  /**
   * Render method.
   * @method render
   * @returns {string} Markup for the component.
   */
  render() {
    const { settings } = config;
    // The next line is only needed for the legacy search component.
    const resultTypeMapper = (contentType) =>
      this.props.contentTypeSearchResultViews[contentType] ||
      this.props.contentTypeSearchResultDefaultView;
    return (
      <Segment basic id="page-search" className="header-wrapper">
        <Helmet title="Search" />
        <Container>
          {this.props.showSearchInput ? (
            <div className="search-input">
              <form onSubmit={this.onSubmit}>
                <TranslatedInput
                  ref={this.inputRef}
                  placeholder={messages.TypeSearchWords}
                  className="searchinput"
                  value={this.state.searchword}
                  onChange={(e) =>
                    this.setState({ searchword: e.target.value })
                  }
                />
                <Button onClick={this.onSubmit}>
                  <FormattedMessage id="Search" defaultMessage="Search" />{' '}
                </Button>
              </form>
            </div>
          ) : null}
          {this.state.allowLocal &&
          getPathPrefix(this.props.history.location) !== undefined ? (
            <LocalCheckbox
              onChange={(checked) => this.setLocal(checked)}
              checked={this.state.local}
            />
          ) : null}
          <SearchResultInfo
            searchableText={this.props.searchableText}
            total={this.props.total}
          />
          <SearchTabs
            groupSelect={this.state.groupSelect}
            setGroupSelect={(groupSelect) => this.setGroupSelect(groupSelect)}
            groupCounts={this.props.groupCounts}
          />
          <article id="content">
            <header>
              {this.props.total > 0 ? (
                <div className="sorting-bar">
                  <SelectSorting
                    value={this.state.active}
                    onChange={(selectedOption, order) => {
                      this.onSortChange(selectedOption, order);
                    }}
                  />
                </div>
              ) : null}
            </header>
            <section id="content-core">
              <div>
                <Dimmer active={this.props.loading} inverted>
                  <Loader indeterminate size="small">
                    <FormattedMessage id="loading" defaultMessage="Loading" />
                  </Loader>
                </Dimmer>
              </div>
              {this.props.items?.map((item, index) => (
                <div key={'' + index + '-' + item['@id']}>
                  {createElement(resultTypeMapper(item['@type']), {
                    key: item['@id'],
                    item,
                  })}
                </div>
              ))}
              {this.props.batching && (
                <div className="search-footer">
                  <Pagination
                    activePage={this.state.currentPage}
                    totalPages={Math.ceil(
                      this.props.total / settings.defaultPageSize,
                    )}
                    onPageChange={this.handleQueryPaginationChange}
                    firstItem={null}
                    lastItem={null}
                    prevItem={{
                      content: <Icon name={paginationLeftSVG} size="18px" />,
                      icon: true,
                      'aria-disabled': !this.props.batching.prev,
                      className: !this.props.batching.prev ? 'disabled' : null,
                    }}
                    nextItem={{
                      content: <Icon name={paginationRightSVG} size="18px" />,
                      icon: true,
                      'aria-disabled': !this.props.batching.next,
                      className: !this.props.batching.next ? 'disabled' : null,
                    }}
                  />
                </div>
              )}
            </section>
          </article>
        </Container>
        {this.state.isClient && (
          <Portal node={document.getElementById('toolbar')}>
            <Toolbar
              pathname={this.props.pathname}
              hideDefaultViewButtons
              inner={<span />}
            />
          </Portal>
        )}
      </Segment>
    );
  }
}

// The xxxWithDefault functions are only to support the legacy search component.
const searchActionWithDefault = (searchAction) =>
  searchAction !== undefined ? searchAction : searchContent;
const getSearchReducerWithDefault = (state, { getSearchReducer }) =>
  getSearchReducer !== undefined ? getSearchReducer(state) : state.search;
const contentTypeSearchResultViewsWithDefault = (
  contentTypeSearchResultViews,
) =>
  contentTypeSearchResultViews !== undefined
    ? contentTypeSearchResultViews
    : {};
const contentTypeSearchResultDefaultViewWithDefault = (
  contentTypeSearchResultDefaultView,
) =>
  contentTypeSearchResultDefaultView !== undefined
    ? contentTypeSearchResultDefaultView
    : DefaultResultItem;

export const __test__ = connect(
  (state, props) => {
    const {
      items,
      total,
      loaded,
      loading,
      batching,
    } = getSearchReducerWithDefault(state, props);
    return {
      items,
      total,
      loaded,
      loading,
      batching,
      intl: state.intl,
      searchableText: qs.parse(props.history.location.search).SearchableText,
      pathname: props.history.location.pathname,
      contentTypeSearchResultViews: contentTypeSearchResultViewsWithDefault(
        props.contentTypeSearchResultViews,
      ),
      contentTypeSearchResultDefaultView: contentTypeSearchResultDefaultViewWithDefault(
        props.contentTypeSearchResultDefaultView,
      ),
    };
  },
  (dispatch, { searchAction }) => ({
    searchContent: (...args) =>
      dispatch(searchActionWithDefault(searchAction)(...args)),
  }),
)(SolrSearch);

export default compose(
  injectIntl,
  connect(
    (state, props) => {
      const {
        items,
        groupCounts,
        total,
        loaded,
        loading,
        batching,
      } = getSearchReducerWithDefault(state, props);
      return {
        items,
        groupCounts,
        total,
        loaded,
        loading,
        batching,
        intl: state.intl,
        searchableText: qs.parse(props.history.location.search).SearchableText,
        pathname: props.history.location.pathname,
        contentTypeSearchResultViews: contentTypeSearchResultViewsWithDefault(
          props.contentTypeSearchResultViews,
        ),
        contentTypeSearchResultDefaultView: contentTypeSearchResultDefaultViewWithDefault(
          props.contentTypeSearchResultDefaultView,
        ),
      };
    },
    (dispatch, { searchAction }) => ({
      searchContent: (...args) =>
        dispatch(searchActionWithDefault(searchAction)(...args)),
    }),
  ),
  asyncConnect([
    {
      key: 'search',
      promise: ({ location, store: { dispatch }, searchAction }) =>
        dispatch(
          searchActionWithDefault(searchAction)('', {
            ...qs.parse(location.search),
            path_prefix: getPathPrefix(location),
            use_site_search_settings: 1,
            metadata_fields: ['effective', 'UID', 'start'],
            hl: 'true',
          }),
        ),
    },
  ]),
)(SolrSearch);
