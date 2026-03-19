import { createContext, useState } from 'react';

export const VocabContext = createContext({
  isVocabRequested: () => false,
  setVocabRequested: () => {},
  resetContext: () => {},
});

export const VocabProvider = ({ children }) => {
  const [value, setValue] = useState({});
  // Note: undefined can be a key here and it represents unilingual vocabularies.
  // In other cases the key represents the language.
  const isVocabRequested = (key, subrequest = undefined) =>
    value[subrequest]?.[key] || value[key] || false;
  const setVocabRequested = (key, subrequest) => {
    // Avoid using setValue as it would trigger a re-render of the component tree.
    if (!value[subrequest]) {
      value[subrequest] = {};
    }
    value[subrequest][key] = true;
  };
  const resetContext = () => {
    setValue({});
  };
  return (
    <VocabContext.Provider
      value={{ isVocabRequested, setVocabRequested, resetContext }}
    >
      {children}
    </VocabContext.Provider>
  );
};
