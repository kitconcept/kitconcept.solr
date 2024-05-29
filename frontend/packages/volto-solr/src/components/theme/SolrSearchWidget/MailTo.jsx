import { useIntl, defineMessages } from 'react-intl';
import { Icon } from '@plone/volto/components';
import mailSVG from '@plone/volto/icons/email.svg';

const messages = defineMessages({
  openMailTo: {
    id: 'Open a Mailto Link to the Members Email Address',
    defaultMessage: 'Open a Mailto Link to the Members Email Address',
  },
});

export default ({ email, className }) => {
  let decoded;
  if (!email.includes('@')) {
    const buffer = Buffer.from(email, 'base64');
    decoded = buffer.toString('ascii');
  }

  const intl = useIntl();

  const rot10 = (s) => {
    return s.replace(
      /[a-z]/g,
      (c) =>
        'abcdefghijklmnopqrstuvwxyz'['klmnopqrstuvwxyzabcdefghij'.indexOf(c)],
    );
  };

  const onClickEmail = (e) => {
    const emailClear = email.includes('@') ? email : rot10(decoded);
    window.open(`mailto:${emailClear}`, '_self');
    e.preventDefault();
    e.stopPropagation();
  };

  return (
    <span
      className={className}
      onClick={(e) => onClickEmail(e)}
      onKeyDown={(e) => {
        if (e.key === 'Enter') {
          onClickEmail();
        }
      }}
      title={intl.formatMessage(messages.openMailTo)}
      role="button"
      tabIndex={0}
    >
      <Icon className="mail" color="#555555" size="24px" name={mailSVG} />
      E-Mail
    </span>
  );
};
