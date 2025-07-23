import { Icon } from '@plone/volto/components';
import config from '@plone/volto/registry';

const IconForContentType = ({ type }) => (
  <Icon
    className="itemIcon"
    size="20px"
    name={
      config.settings.contentTypeSearchResultIcons[type] ||
      config.settings.contentTypeSearchResultDefaultIcon
    }
  />
);

export default IconForContentType;
