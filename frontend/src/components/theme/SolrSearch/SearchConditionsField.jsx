import { SearchConditionsValue } from './SearchConditionsValue';
import { useCallback, useMemo } from 'react';
import { ShowMoreIndicator } from './ShowMoreIndicator';
import { SearchConditionsFieldSearch } from './SearchConditionsFieldSearch';
import { useIntl } from 'react-intl';

// Hardcoded ATM and MUST match the value in kitconcept.solr
const limit_less = 5;

const empty = {};

const getIntlMessage = (id) => ({ id, defaultMessage: id });

export const SearchConditionsField = ({
  fieldDef,
  values: v,
  conditionTree: c,
  setCondition: setC,
  setContains: setP,
  setMore: setM,
}) => {
  const intl = useIntl();
  const { name } = fieldDef;
  const setCondition = useCallback(
    (value, checked) => setC(name, value, checked),
    [setC, name],
  );
  const condition = useMemo(() => c[name]?.c || empty, [c, name]);
  const setContains = (contains) => setP(name, contains);
  const contains = c[name]?.p;
  const setMore = (more) => setM(name, more);
  const more = c[name]?.m;

  // Strip the last value which is appended to signal that
  // there are more values
  const hasMore = !more && v.length > limit_less;
  if (hasMore) {
    v = v.slice(0, limit_less);
  }

  // Sorting values by count, alphabetic
  const selectValues = useMemo(
    () =>
      v.toSorted(
        ([aLabel, aCount], [bLabel, bCount]) =>
          Math.sign(bCount - aCount) * 2 +
          Math.sign(aLabel.localeCompare(bLabel)),
      ),
    [v],
  );

  const remainingSelected = useMemo(
    () =>
      Object.entries(
        selectValues.reduce(
          (remaining, [value, _]) => ({
            ...remaining,
            [value]: false,
          }),
          condition,
        ),
      ).reduce(
        (remainingSelected, [name, check]) =>
          check ? remainingSelected.concat([name]) : remainingSelected,
        [],
      ),
    [condition, selectValues],
  );

  const values = useMemo(
    () => selectValues.concat(remainingSelected.map((value) => [value, null])),
    [selectValues, remainingSelected],
  );

  return useMemo(
    () => (
      <div className="searchConditionsField">
        <div className="searchConditionsFieldHeader">
          {intl.formatMessage(getIntlMessage(fieldDef.label ?? fieldDef.name))}
          <SearchConditionsFieldSearch
            value={contains}
            setValue={setContains}
          />
        </div>
        <div className="searchConditionsFieldContent">
          {values.map(([value, counter], index) => (
            <SearchConditionsValue
              key={index}
              fieldDef={fieldDef}
              value={value}
              counter={counter}
              condition={condition}
              setCondition={setCondition}
            />
          ))}
        </div>
        <div className="searchConditionsFieldFooter">
          {(more || hasMore) && (
            <ShowMoreIndicator value={more} setValue={setMore} />
          )}
        </div>
      </div>
    ),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [
      // eslint-disable-next-line react-hooks/exhaustive-deps
      JSON.stringify(fieldDef),
      // eslint-disable-next-line react-hooks/exhaustive-deps
      JSON.stringify(values),
      // eslint-disable-next-line react-hooks/exhaustive-deps
      contains,
      // eslint-disable-next-line react-hooks/exhaustive-deps
      more,
      // eslint-disable-next-line react-hooks/exhaustive-deps
      JSON.stringify(condition),
    ],
  );
};
