import { FormattedMessage } from 'react-intl';
import solrConfig from './solr-config';
import messages from './solr-facets-i18n';

export const SearchTabs = ({ groupSelect, setGroupSelect, groupCounts }) => {
  groupCounts = groupCounts || [];
  return (
    <div className="searchTabs ui top attached tabular menu">
      {solrConfig.searchTabs.map((item, index) => {
        const isActive = index === groupSelect;
        const hasResults = groupCounts[index];
        return (
          <span
            onClick={() => hasResults && setGroupSelect(index)}
            onKeyDown={() => hasResults && setGroupSelect(index)}
            role="button"
            tabIndex={index}
            key={index}
            className={
              'searchTab item' +
              (isActive ? ' active' : ' inactive') +
              (hasResults ? ' results' : ' noresults')
            }
          >
            <span>
              {messages[item.label] ? (
                <FormattedMessage {...messages[item.label]} />
              ) : (
                item.label
              )}
              <span
                className={
                  'searchCounter ui circular label ' +
                  (isActive ? ' blue' : 'white')
                }
              >
                {hasResults ? groupCounts[index] : '0'}
              </span>
            </span>
          </span>
        );
      })}
    </div>
  );
};
