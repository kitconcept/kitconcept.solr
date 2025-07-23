import { injectLazyLibs } from '@plone/volto/helpers/Loadable/Loadable';
import { Icon } from '@plone/volto/components';
import downSVG from './icons/down-key-nofill.svg';
import upSVG from './icons/up-key-nofill.svg';

export const DropdownIndicator = injectLazyLibs('reactSelect')((props) => {
  const { DropdownIndicator } = props.reactSelect.components;
  return (
    <DropdownIndicator {...props}>
      {props.selectProps.menuIsOpen ? (
        <Icon name={upSVG} size="10px" color="current" />
      ) : (
        <Icon name={downSVG} size="10px" color="current" />
      )}
    </DropdownIndicator>
  );
});
