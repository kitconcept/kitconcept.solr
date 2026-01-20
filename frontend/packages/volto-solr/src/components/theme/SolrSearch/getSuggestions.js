const concat = (a) => [].concat(...a);

export const getSuggestions = (suggestions, options = {}) => {
  const maxLength = options?.maxLength ?? 4;
  const getter = options?.getter ?? ((i) => i.word);
  const sorter = options?.sorter ?? ((a, b) => b.freq - a.freq);
  return concat(
    suggestions
      .filter((_, index) => index % 2 === 1)
      .map((suggestionItem) => suggestionItem.suggestion),
  )
    .sort((a, b) => getter(a)?.localeCompare(getter(b)))
    .filter(function (item, pos, ary) {
      const word = getter(item);
      return word && (!pos || word !== getter(ary[pos - 1]));
    })
    .sort(sorter)
    .map((item) => getter(item))
    .slice(0, maxLength);
};
