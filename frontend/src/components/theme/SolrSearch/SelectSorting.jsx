import { useMemo } from 'react';
import { useIntl, defineMessages } from 'react-intl';
import { injectLazyLibs } from '@plone/volto/helpers/Loadable/Loadable';
import {
  customSelectStyles,
  selectTheme,
} from '@plone/volto/components/manage/Widgets/SelectStyling';
import { DropdownIndicator } from './DropdownIndicator';

const messages = defineMessages({
  sortBy: {
    id: 'Sort By:',
    defaultMessage: 'Sort by:',
  },
  select: {
    id: 'Select…',
    defaultMessage: 'Select…',
  },
  relevance: {
    id: 'Relevance',
    defaultMessage: 'Relevance',
  },
  alphabetically: { id: 'Alphabetically', defaultMessage: 'Alphabetically' },
  newestFirst: {
    id: 'Date (newest first)',
    defaultMessage: 'Date (newest first)',
  },
});

export const SelectSorting = injectLazyLibs(['reactSelect'])(
  ({ onChange, value, reactSelect }) => {
    const intl = useIntl();
    const Select = reactSelect.default;
    const choices = [
      {
        value: 'relevance',
        label: intl.formatMessage(messages.relevance),
      },
      {
        value: 'sortable_title',
        label: intl.formatMessage(messages.alphabetically),
      },
      {
        value: 'effective',
        label: intl.formatMessage(messages.newestFirst),
      },
    ];

    const choicesByValue = useMemo(
      () =>
        choices.reduce((d, v) => {
          d[v.value] = v;
          return d;
        }, {}),
      [choices],
    );

    return (
      <span className="sort-field">
        <span className="sort-by">{intl.formatMessage(messages.sortBy)}</span>
        <div className="sort-select">
          <Select
            id="sort_by"
            name="sort_by"
            isSearchable={true}
            className="react-select-container"
            classNamePrefix="react-select"
            isMulti={false}
            options={choices}
            styles={customSelectStyles}
            theme={selectTheme}
            components={{
              DropdownIndicator,
            }}
            value={choicesByValue[value]}
            placeholder={intl.formatMessage(messages.select)}
            onChange={({ value }) =>
              onChange
                ? onChange(value, value === 'effective' ? 'reverse' : undefined)
                : undefined
            }
          />
        </div>
      </span>
    );
  },
);
