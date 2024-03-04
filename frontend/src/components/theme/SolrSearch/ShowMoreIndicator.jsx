import { useCallback } from 'react';
import { Icon } from '@plone/volto/components';
import downSVG from './icons/down-key-nofill.svg';
import upSVG from './icons/up-key-nofill.svg';
import { useIntl, defineMessages } from 'react-intl';

const messages = defineMessages({
  showMore: {
    // Mehr anzeigen
    id: 'Show more',
    defaultMessage: 'Show more',
  },
  showLess: {
    // Weniger anzeigen
    id: 'Show less',
    defaultMessage: 'Show less',
  },
});

export const ShowMoreIndicator = ({ value, setValue }) => {
  const intl = useIntl();
  const onClick = useCallback((evt) => setValue((v) => !v), [setValue]);
  return (
    <span
      className="showMoreIndicator"
      onClick={onClick}
      onKeyDown={() => {}}
      role="button"
      tabindex="0"
    >
      {value ? (
        <>
          {intl.formatMessage(messages.showLess)}
          <Icon name={upSVG} size="10px" color="current" />
        </>
      ) : (
        <>
          {intl.formatMessage(messages.showMore)}
          <Icon name={downSVG} size="10px" color="current" />
        </>
      )}
    </span>
  );
};
