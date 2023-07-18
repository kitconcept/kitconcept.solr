import { FormattedMessage } from 'react-intl';
import messages from './solr-facets-i18n';

export const SearchTabs = ({ groupSelect, setGroupSelect, facetGroups }) => {
  facetGroups = facetGroups || [];
  return (
    <div className="searchTabs ui top attached tabular menu">
      {facetGroups.map(([label, counter], index) => {
        const isActive = index === groupSelect;
        const hasResults = counter;
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
              {messages[label] ? (
                <FormattedMessage {...messages[label]} />
              ) : (
                label
              )}
              <span
                className={
                  'searchCounter ui circular label ' +
                  (isActive ? ' blue' : 'white')
                }
              >
                {hasResults ? counter : '0'}
              </span>
            </span>
          </span>
        );
      })}
    </div>
  );
};
