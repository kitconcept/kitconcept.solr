import {
  decodeConditionTree,
  encodeConditionTree,
  pruneConditionTree,
} from './SearchConditions';

export const queryStateFromParams = (params) => ({
  searchword: params.SearchableText || '',
  sortOn: params.sort_on || 'relevance',
  sortOrder: params.sort_order || '',
  groupSelect: parseInt(params.group_select) || 0,
  allowLocal: (params.allow_local || '').toLowerCase() === 'true',
  local: (params.local || '').toLowerCase() === 'true',
  facetConditions: decodeConditionTree(params.facet_conditions, {
    catchError: true,
  }),
  // Passed through opaquely: consumed by the backend (the dialog's
  // filter chips arrive with it), but kept in the query state so
  // in-page interactions (sort, paging) do not drop it from the URL.
  extraConditions: params.extra_conditions || '',
});

export const queryStateToParams = (queryState) => ({
  SearchableText: queryState.searchword,
  sort_on: queryState.sortOn,
  sort_order: queryState.sortOrder,
  group_select: '' + queryState.groupSelect,
  allow_local: '' + (queryState.allowLocal || false),
  local: '' + (queryState.local || false),
  facet_conditions: encodeConditionTree(
    pruneConditionTree(queryState.facetConditions),
  ),
  extra_conditions: queryState.extraConditions || '',
});
