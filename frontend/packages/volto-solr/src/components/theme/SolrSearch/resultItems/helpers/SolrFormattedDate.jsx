import { useIntl } from 'react-intl';

const SolrFormattedDate = ({ date, showTime }) => {
  const intl = useIntl();
  return new Intl.DateTimeFormat(intl.locale, {
    dateStyle: 'medium',
    ...(showTime ? { timeStyle: 'short' } : undefined),
  }).format(new Date(date));
};

export default SolrFormattedDate;
