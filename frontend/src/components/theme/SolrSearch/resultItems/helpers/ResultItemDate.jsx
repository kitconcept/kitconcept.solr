import React from 'react';
import { format, parse, deLocale, enLocale } from 'date-fns';
import { useIntl } from 'react-intl';

// Add one day to the earliest date to make sure that differences
// because of timezones are still under the threshold
const thresholdDate = new Date(null);
thresholdDate.setDate(thresholdDate.getDate() + 1);

const ResultItemDate = ({ date, hasExcerpt, showTime }) => {
  const intl = useIntl();
  // Do not display dates of unix datestamp zero. (default)
  // Also tolerate a one day margin, because the earliest date in UTC
  // might come with a bit of difference because of timezones.
  // e.g. "1969-12-30T23:00:00Z" in UTC+01 instead of 1969-12-30T00:00:00Z"
  // This _might_ occur due to conversion problem in the solr result,
  // but in general we don't care as we only consider a granularity of days.
  return new Date(date) > thresholdDate ? (
    <span className="date">
      {intl.locale === 'de'
        ? format(parse(date), showTime ? 'DD.MM.YYYY HH:mm' : 'DD.MM.YYYY', {
            locale: deLocale,
          }) + (showTime ? ' Uhr' : '')
        : format(parse(date), showTime ? 'DD/MM/YYYY HH:mm' : 'DD/MM/YYYY', {
            locale: enLocale,
          })}
      {hasExcerpt ? ' — ' : ' '}
    </span>
  ) : null;
};

export default ResultItemDate;
