import { getVocabulary } from '@plone/volto/actions/vocabularies/vocabularies';
import { useDispatch, useSelector, shallowEqual } from 'react-redux';
import { useEffect, useContext } from 'react';
import { VocabContext } from './VocabContext';

// Has to be immutable, avoids unnecessary re-renders.
const emptyArray = [];

const _useVocabs = (arrayOfOptions, hookName) => {
  if (!Array.isArray(arrayOfOptions)) {
    throw new Error(
      `${hookName}: array of options is required, [{ name, isMultilingual }, ...] is expected [got: ${JSON.stringify(arrayOfOptions)}]`,
    );
  }
  arrayOfOptions.forEach((options) => {
    if (options === undefined || typeof options !== 'object') {
      throw new Error(
        `${hookName}: options must be an object, { name, isMultilingual } is expected [got: ${JSON.stringify(options)}]`,
      );
    }
  });
  arrayOfOptions.forEach((options) => {
    if (!options.name) {
      throw new Error(
        `${hookName}: name is required [got: ${JSON.stringify(options)}]`,
      );
    }
  });
  const dispatch = useDispatch();
  const { isVocabRequested, setVocabRequested } = useContext(VocabContext);

  // Language will be undefined for unilingual vocabularies.
  // Object keyed by vocab name.
  const languages = useSelector(
    (state) =>
      arrayOfOptions.reduce((acc, { name, isMultilingual = true }) => {
        acc[name] = isMultilingual ? state.intl.locale : undefined;
        return acc;
      }, {}),
    shallowEqual,
  );

  // Object keyed by vocab name.
  const items = useSelector(
    (state) =>
      arrayOfOptions.reduce((acc, { name, isMultilingual = true }) => {
        const base = state.vocabularies?.[name];
        const language = languages[name];
        acc[name] =
          (isMultilingual ? base?.subrequests?.[language] : base)?.items ||
          emptyArray;
        return acc;
      }, {}),
    shallowEqual,
  );

  useEffect(() => {
    arrayOfOptions.forEach(({ name }) => {
      const language = languages[name];
      if (items[name].length === 0 && !isVocabRequested(name, language)) {
        setVocabRequested(name, language);
        dispatch(
          getVocabulary({
            vocabNameOrURL: name,
            size: -1,
            subrequest: language,
          }),
        );
      }
    });
  }, [
    dispatch,
    items,
    languages,
    isVocabRequested,
    setVocabRequested,
    arrayOfOptions,
  ]);

  return items;
};

export const useVocab = (options) =>
  _useVocabs([options], 'useVocab')[options.name];
export const useVocabs = (options) => _useVocabs(options, 'useVocabs');
