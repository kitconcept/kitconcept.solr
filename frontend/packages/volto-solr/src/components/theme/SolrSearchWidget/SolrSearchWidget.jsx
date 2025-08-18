/**
 * Solr Search widget component.
 * @module components/theme/SearchWidget/SearchWidget
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { withRouter, Link } from 'react-router-dom';
import { Form } from 'semantic-ui-react';
import { compose } from 'redux';
import {
  defineMessages,
  injectIntl,
  FormattedMessage,
  useIntl,
} from 'react-intl';
import { useDispatch, useSelector } from 'react-redux';
import { solrSearchSuggestions } from '../../../actions';
import Autosuggest from 'react-autosuggest';
import cx from 'classnames';
import MailTo from './MailTo';

import { flattenToAppURL } from '@plone/volto/helpers';
import { Icon } from '@plone/volto/components';
import qs from 'query-string';
import config from '@plone/volto/registry';

import searchSVG from '../../../icons/search.svg';
import personSVG from '../../../icons/person.svg';
import debounce from 'lodash.debounce';

const messages = defineMessages({
  search: {
    id: 'Search',
    defaultMessage: 'Search',
  },
  searchSite: {
    id: 'Search Site',
    defaultMessage: 'Search Site',
  },
  showAllSearchResults: {
    id: 'Show all search results...',
    defaultMessage: 'Show all search results...',
  },
});

// --
// SolrSearchAutosuggest is factored ouf from SolrSearchWidget, and it contains
// only the input field, so we can include it better from Search.jsx.
// --

const ID_ALL = '@ALL';
// Items to show. Note this must be <= 10 as 10 items will
// always be fetched currently.
const NR_ITEMS = 8;

const SolrSearchAutosuggestRaw = (props) => {
  const originalText = props.value;
  const dispatch = useDispatch();
  let suggestions = useSelector((state) =>
    state.solrSearchSuggestions.items.slice(0, NR_ITEMS),
  ).concat({
    '@type': 'ShowAll',
    '@id': ID_ALL,
    title: originalText,
  });

  const shortenURL = (url) => {
    const arr = url.split('/');
    let str;
    if (arr.length >= 5) {
      str = `${arr[0]}/${arr[1]}/${arr[2]}/... /${arr.pop()}`;
    } else {
      arr.pop();
      str = arr.join('/');
    }
    return '/' + str;
  };

  const renderSuggestion = (suggestion) => {
    const getIcon = (type) =>
      config.settings.contentTypeSearchResultIcons[type] ||
      config.settings.contentTypeSearchResultDefaultIcon;
    const getContentTypeTitle = (contentType) =>
      props.intl.formatMessage({
        id: contentType,
        defaultMessage: contentType,
      });

    return (
      <>
        {suggestion['@type'] === 'ShowAll' && suggestions.length > 1 ? (
          <button className="all-results-button">
            <FormattedMessage {...messages.showAllSearchResults} />
          </button>
        ) : suggestion['@type'] === 'Member' ? (
          <div className="member suggestion">
            <Link
              className="image-wrapper"
              to={flattenToAppURL(suggestion['@id'])}
            >
              {suggestion.image ? (
                <img
                  width="40"
                  height="40"
                  src={suggestion.image.scales.thumb.download}
                  alt={suggestion.title}
                />
              ) : (
                <div className="icon-wrapper placeholder">
                  <Icon name={personSVG} size="40px" />
                </div>
              )}
            </Link>
            <div className="member-body">
              <Link
                to={flattenToAppURL(suggestion['@id'])}
                className="member-title"
              >
                {`${suggestion.salutation ? suggestion.salutation : ''} ${
                  suggestion.academic ? suggestion.academic : ''
                }
                  ${suggestion.title}`}
              </Link>
              <div className="member-info">
                {suggestion.phone && (
                  <span>Tel. {suggestion.phone} |&nbsp;</span>
                )}
                {suggestion.email && (
                  <MailTo email={suggestion.email} className="mail" />
                )}
                {suggestion.institute && (
                  <span>{suggestion.institute} |&nbsp;</span>
                )}
                <span>
                  {suggestion.building && `Geb.${suggestion.building}`}
                  {suggestion.room && `/R.${suggestion.room}`}
                </span>
              </div>
            </div>
          </div>
        ) : (
          suggestion['@type'] !== 'ShowAll' && (
            <div
              className="suggestion"
              to={flattenToAppURL(suggestion['@id']).split('/')}
            >
              <div className="icon-wrapper">
                <Icon name={getIcon(suggestion['@type'])} size="30px" />
                <span className="icon-title">
                  {getContentTypeTitle(suggestion['@type'])}
                </span>
              </div>
              <div className="suggestion-wrapper">
                <div className="suggestion-path">
                  {shortenURL(flattenToAppURL(suggestion['@id']))}
                </div>
                <div className="suggestion-title">{suggestion.title}</div>
              </div>
            </div>
          )
        )}
      </>
    );
  };

  const cancelRequest = useRef(null);
  const debounceCustom = useRef(
    debounce((value) => {
      if (cancelRequest.current) {
        cancelRequest.current.request.abort();
        cancelRequest.current = null;
      }
      cancelRequest.current = dispatch(solrSearchSuggestions(value));
    }, 300),
  );

  const onSuggestionsFetchRequested = ({ value, reason }) => {
    debounceCustom.current(value);

    if (reason === 'suggestion-selected') {
      props.history.push(flattenToAppURL(value['@id']));
    }
  };

  const getSuggestionValue = (suggestion) => suggestion;

  const onSubmit = (event) => {
    if (props.inputRef) {
      //    props.inputRef.current.value = '';
      // Only search when text is provided - do not navigate to empty search results.
      // Important: Blur the input, otherwise the dropdown will reopen and never close.
      props.inputRef.current.blur();
    }
    if (props.onSubmit) {
      props.onSubmit(event);
    }
    event.preventDefault();
  };

  const ref = useRef();

  // react-autosuggest does not seem to support an onSubmit handler
  const onKeyDown = (event) => {
    if (event.key === 'Enter') {
      // We want to onSubmit **ONLY** when enter is pressed in the input.
      // NOT when enter is pressed on any of the drowdown items, or on the
      // All Items line. This makes sure that the dialog disappears when
      // we pressed enter in the input, but pressing input on any other
      // line does the navigation as it should.
      const { highlightedSuggestionIndex } = ref.current?.state;
      if (highlightedSuggestionIndex == null) {
        onSubmit(event);
        return false;
      }
    }
    return true;
  };

  const onSuggestionSelected = (
    event,
    { suggestion, suggestionValue, suggestionIndex, sectionIndex, method },
  ) => {
    const id = suggestion['@id'];
    if (id === ID_ALL) {
      onSubmit(event);
      event.preventDefault();
    } else {
      props.history.push(flattenToAppURL(id));
      event.preventDefault();
    }
  };

  const inputProps = {
    placeholder: props.placeholder,
    value: props.value,
    onChange: props.onChange,
    onFocus: props.onFocus,
    onBlur: props.onBlur,
    onKeyDown: onKeyDown,
  };

  const storeInputReference = (autosuggest) => {
    if (autosuggest) {
      if (props.inputRef) {
        props.inputRef.current = autosuggest.input;
      }
      ref.current = autosuggest;
    }
  };

  return (
    <Autosuggest
      className="search-input"
      ref={storeInputReference}
      suggestions={suggestions || []}
      onSuggestionsFetchRequested={onSuggestionsFetchRequested}
      onSuggestionsClearRequested={() => {}}
      renderSuggestion={renderSuggestion}
      getSuggestionValue={getSuggestionValue}
      inputProps={inputProps}
      onSuggestionSelected={onSuggestionSelected}
      onSubmit={onSubmit}
    />
  );
};

export const SolrSearchAutosuggest = compose(
  withRouter,
  injectIntl,
)(SolrSearchAutosuggestRaw);

// --
// SolrSearchWidget would be needed if we wanted the search widget
// in the header of each page, as originally supported by Volto.
// --

const SolrSearchWidget = (props) => {
  const intl = useIntl();
  const [focused, setFocused] = useState(false);
  const chainedOnFocus = props?.onFocus;
  const onFocus = useCallback(() => {
    setFocused(true);
    if (chainedOnFocus) {
      chainedOnFocus();
    }
  }, [setFocused, chainedOnFocus]);
  const chainedOnBlur = props?.onBlur;
  const onBlur = useCallback(() => {
    setFocused(false);
    if (chainedOnBlur) {
      chainedOnBlur();
    }
  }, [setFocused, chainedOnBlur]);
  const [text, setText] = useState('');
  // const [originalText, setOriginalText] = useState('');

  const onChange = (event, { newValue, method }) => {
    // method === 'type' && setOriginalText(newValue);
    typeof newValue === 'string' ? setText(newValue) : setText(newValue.title);
  };

  useEffect(() => {
    if (props.location.pathname === '/search') {
      const SearchableText = qs.parse(props.location.search)?.SearchableText;
      if (SearchableText?.length > 0 && text.length === 0) {
        setText(SearchableText);
      }
    } else {
      setText('');
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [props.location.pathname]);

  const onSubmit = (event) => {
    // Only search when text is provided - do not navigate to empty search results.
    if (text) {
      props.history.push(
        `/search?SearchableText=${text}&metadata_fields=room&metadata_fields=building&metadata_fields=phone&metadata_fields=email&metadata_fields=getIcon&metadata_fields=institute`,
      );
    }
    event.preventDefault();
  };

  return (
    <div className={cx('search-widget', { focused })}>
      <Form action="/search" onSubmit={onSubmit} className="">
        <Form.Field className="searchbox">
          <SolrSearchAutosuggest
            {...props}
            value={text ? text : ''}
            onChange={onChange}
            onFocus={onFocus}
            onBlur={onBlur}
            onSubmit={onSubmit}
            placeholder={props.intl.formatMessage(messages.searchSite)}
          />
          <button aria-label={intl.formatMessage(messages.search)}>
            <Icon name={searchSVG} />
          </button>
        </Form.Field>
      </Form>
    </div>
  );
};

export default compose(withRouter, injectIntl)(SolrSearchWidget);
