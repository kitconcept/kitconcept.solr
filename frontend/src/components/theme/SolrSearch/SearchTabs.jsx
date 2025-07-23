import { useIntl } from 'react-intl';

export const SearchTabs = ({ groupSelect, setGroupSelect, facetGroups }) => {
  facetGroups = facetGroups || [];
  const intl = useIntl();
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
              {intl.formatMessage({ id: label, defaultMessage: label })}
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
