import { SearchConditionsField } from './SearchConditionsField';
import { useCallback, useMemo } from 'react';
import { bToA, aToB } from './base64Helpers';

function isEmpty(obj) {
  for (const prop in obj) {
    if (Object.hasOwn(obj, prop)) {
      return false;
    }
  }
  return true;
}

export const encodeConditionTree = (conditionTree) =>
  isEmpty(conditionTree) ? '' : bToA(JSON.stringify(conditionTree));

export const decodeConditionTree = (encoded, { catchError } = {}) => {
  if (encoded) {
    try {
      return JSON.parse(aToB(encoded));
    } catch (exc) {
      if (catchError) {
        // eslint-disable-next-line no-console
        console.warn(
          `Ignored broken facet_conditions value [${encoded}] [${exc.message}]`,
        );
      } else {
        throw exc;
      }
    }
  }
  return {};
};

const prunedField = (fieldName, v) =>
  isEmpty(v) ? undefined : { [fieldName]: v };

export const pruneConditionTree = (conditionTree) =>
  Object.entries(conditionTree).reduce(
    (condition, [fieldName, field]) => ({
      ...condition,
      ...prunedField(fieldName, {
        ...prunedField(
          'c',
          Object.entries(field.c || {}).reduce(
            (fieldC, [value, checked]) => ({
              ...fieldC,
              ...(checked ? { [value]: true } : undefined),
            }),
            {},
          ),
        ),
        ...(field.p ? { p: field.p } : undefined),
        ...(field.m ? { m: true } : undefined),
      }),
    }),
    {},
  );

export const SearchConditions = ({
  groupSelect,
  facetFields,
  conditionTree = {},
  setConditionTree = () => {},
}) => {
  facetFields = facetFields || [];

  const setCondition = useCallback(
    (fieldName, value, checked) =>
      setConditionTree((conditionTree) => ({
        ...conditionTree,
        [fieldName]: {
          ...(conditionTree[fieldName] || {}),
          c: {
            ...(conditionTree[fieldName]?.c || {}),
            [value]: checked,
          },
        },
      })),
    [setConditionTree],
  );

  const setContains = useCallback(
    (fieldName, contains) =>
      setConditionTree((conditionTree) => ({
        ...conditionTree,
        [fieldName]: {
          ...(conditionTree[fieldName] || {}),
          p: contains,
        },
      })),
    [setConditionTree],
  );

  const setMore = useCallback(
    (fieldName, more) =>
      setConditionTree((conditionTree) => ({
        ...conditionTree,
        [fieldName]: {
          ...(conditionTree[fieldName] || {}),
          m: more(conditionTree[fieldName]?.m),
        },
      })),
    [setConditionTree],
  );

  return useMemo(
    () =>
      facetFields.length > 0 ? (
        <div className="searchConditions ui">
          {facetFields.map(([fieldDef, values], index) => (
            <SearchConditionsField
              key={index}
              fieldDef={fieldDef}
              values={values}
              conditionTree={conditionTree}
              setCondition={setCondition}
              setContains={setContains}
              setMore={setMore}
            />
          ))}
        </div>
      ) : null,
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [JSON.stringify(facetFields), conditionTree],
  );
};
