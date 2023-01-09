import { defineMessages, FormattedMessage } from 'react-intl';

const messages = defineMessages({
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

export const SearchResultInfo = ({ searchableText, total }) => (
  <div className="total-bar">
    <span className="results">
      {searchableText ? (
        <FormattedMessage {...messages.totalResultsFor} values={{ total }} />
      ) : (
        <FormattedMessage {...messages.totalResults} values={{ total }} />
      )}
    </span>
    <h2>{searchableText || '\u00A0'}</h2>
  </div>
);
