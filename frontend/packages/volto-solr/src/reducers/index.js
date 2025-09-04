import solrsearch from './solrsearch/solrsearch';
import solrSearchSuggestions from './solrsearch/solrSearchSuggestions';
import { defineMessages } from 'react-intl';

// needed to add as overrides are not parsed by i18n
defineMessages({
  sortBy: {
    id: 'Sort By:',
    defaultMessage: 'Sort by:',
  },
  select: {
    id: 'Select…',
    defaultMessage: 'Select…',
  },
  relevance: {
    id: 'Relevance',
    defaultMessage: 'Relevance',
  },
  alphabetically: { id: 'Alphabetically', defaultMessage: 'Alphabetically' },
  newestFirst: {
    id: 'Date (newest first)',
    defaultMessage: 'Date (newest first)',
  },
  totalResultsFor: {
    id: '{total, plural, =0 {No results} =1 {# result} other {# results}} for',
    defaultMessage:
      '{total, plural, =0 {No results} =1 {# result} other {# results}} for',
  },
  totalResults: {
    id: '{total, plural, =0 {No results} =1 {# result} other {# results}}',
    defaultMessage:
      '{total, plural, =0 {No results} =1 {# result} other {# results}}',
  },
});

const reducers = {
  solrsearch,
  solrSearchSuggestions,
};

export default reducers;
