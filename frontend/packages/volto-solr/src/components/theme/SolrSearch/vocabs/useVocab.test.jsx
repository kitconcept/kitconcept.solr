import { renderHook } from '@testing-library/react-hooks';
import { waitFor } from '@testing-library/react';
import { Provider, useDispatch } from 'react-redux';
import { getVocabulary } from '@plone/volto/actions/vocabularies/vocabularies';
import { useVocab, useVocabs } from './useVocab';
import { VocabContext } from './VocabContext';
import configureStore from 'redux-mock-store';

jest.mock('react-redux', () => {
  const mod = jest.requireActual('react-redux');
  return {
    ...mod,
    useDispatch: jest.fn(),
  };
});

jest.mock('@plone/volto/actions/vocabularies/vocabularies', () => ({
  getVocabulary: jest.fn(),
}));

const mockStore = configureStore();

const isVocabRequested = jest.fn();
const setVocabRequested = jest.fn();
const resetContext = jest.fn();

const mockVocabContext = {
  isVocabRequested,
  setVocabRequested,
  resetContext,
};

let store = mockStore({});
const wrapper = ({ children }) => (
  <Provider store={store}>
    <VocabContext.Provider value={mockVocabContext}>
      {children}
    </VocabContext.Provider>
  </Provider>
);

const describeWithVocabData =
  (options, items, data, subrequests, setVocabRequestedParams) => () => {
    let mockDispatch = jest.fn();

    beforeEach(() => {
      jest.clearAllMocks();
      mockDispatch = jest.fn(() =>
        Promise.resolve({
          // it does not matter what we return here,
          // as we are not using the result
          items: [],
        }),
      );
      useDispatch.mockReturnValue(mockDispatch);

      store = mockStore({
        vocabularies: {
          'kitconcept.intranet.vocabularies.test': {
            items: [],
          },
        },
        intl: { locale: 'en' },
      });

      isVocabRequested.mockReturnValue(false);
    });

    it('should dispatch getVocabulary when vocab is not loaded', async () => {
      const { result, rerender } = renderHook(
        () =>
          useVocab({
            name: 'kitconcept.intranet.vocabularies.test',
            ...options,
          }),
        { wrapper },
      );

      rerender();

      await waitFor(() => {
        expect(getVocabulary).toHaveBeenCalledWith({
          vocabNameOrURL: 'kitconcept.intranet.vocabularies.test',
          size: -1,
          ...subrequests,
        });
      });

      expect(result.current).toEqual([]);
    });

    it('should return vocab items when vocab is loaded', async () => {
      store = mockStore({
        vocabularies: {
          'kitconcept.solr.vocabularies.test': data,
        },
        intl: { locale: 'en' },
      });

      const { result } = renderHook(
        () =>
          useVocab({ name: 'kitconcept.solr.vocabularies.test', ...options }),
        { wrapper },
      );

      expect(result.current).toEqual(items);
    });

    describe('if used within a vocab context', () => {
      it('should not dispatch getVocabulary if vocab is already requested', async () => {
        isVocabRequested.mockReturnValue(true);

        const { result } = renderHook(
          () =>
            useVocab({ name: 'kitconcept.solr.vocabularies.test', ...options }),
          { wrapper },
        );

        expect(getVocabulary).not.toHaveBeenCalled();
        expect(result.current).toEqual([]);
      });

      it('should dispatch getVocabulary and set the vocab as requested, when vocab is not loaded', async () => {
        isVocabRequested.mockReturnValue(false);

        const { result, rerender } = renderHook(
          () =>
            useVocab({ name: 'kitconcept.solr.vocabularies.test', ...options }),
          { wrapper },
        );

        rerender();

        await waitFor(() => {
          expect(getVocabulary).toHaveBeenCalledWith({
            vocabNameOrURL: 'kitconcept.solr.vocabularies.test',
            size: -1,
            ...subrequests,
          });
        });

        expect(result.current).toEqual([]);
        expect(setVocabRequested).toHaveBeenCalledWith(
          'kitconcept.solr.vocabularies.test',
          ...setVocabRequestedParams,
        );
      });

      it('should return vocab items when vocab is loaded', async () => {
        store = mockStore({
          vocabularies: {
            'kitconcept.solr.vocabularies.test': data,
          },
          intl: { locale: 'en' },
        });

        isVocabRequested.mockReturnValue(true);

        const { result } = renderHook(
          () =>
            useVocab({ name: 'kitconcept.solr.vocabularies.test', ...options }),
          { wrapper },
        );

        expect(result.current).toEqual(items);
      });
    });
  };

describe('useVocab Hook', () => {
  describe('validation', () => {
    it('should throw when options is undefined', () => {
      const { result } = renderHook(() => useVocab(undefined), { wrapper });
      expect(result.error).toEqual(
        new Error(
          'useVocab: options must be an object, { name, isMultilingual } is expected [got: undefined]',
        ),
      );
    });

    it('should throw when options is not an object', () => {
      const { result } = renderHook(() => useVocab('a string'), { wrapper });
      expect(result.error).toEqual(
        new Error(
          'useVocab: options must be an object, { name, isMultilingual } is expected [got: "a string"]',
        ),
      );
    });

    it('should throw when name is not provided', () => {
      const { result } = renderHook(() => useVocab({ isMultilingual: true }), {
        wrapper,
      });
      expect(result.error).toEqual(
        new Error('useVocab: name is required [got: {"isMultilingual":true}]'),
      );
    });
  });

  const items = [
    { value: 'K1', label: 'Test Item 1' },
    { value: 'K2', label: 'Test Item 2' },
  ];

  const data = {
    items,
  };

  describe(
    'no multilingual',
    describeWithVocabData({ isMultilingual: false }, items, data, {}, [
      undefined,
    ]),
  );

  const multilingualData = {
    subrequests: {
      en: { items },
    },
  };

  describe(
    'isMultilingual',
    describeWithVocabData(
      { isMultilingual: true },
      items,
      multilingualData,
      {
        subrequest: 'en',
      },
      ['en'],
    ),
  );

  describe(
    'isMultilingual',
    describeWithVocabData(
      undefined,
      items,
      multilingualData,
      {
        subrequest: 'en',
      },
      ['en'],
    ),
  );
});

describe('useVocabs Hook', () => {
  const items1 = [{ value: 'A1', label: 'Item A1' }];
  const items2 = [{ value: 'B1', label: 'Item B1' }];

  describe('validation', () => {
    it('should throw when argument is not an array', () => {
      const { result } = renderHook(() => useVocabs('not an array'), {
        wrapper,
      });
      expect(result.error).toEqual(
        new Error(
          'useVocabs: array of options is required, [{ name, isMultilingual }, ...] is expected [got: "not an array"]',
        ),
      );
    });

    it('should throw when an element is not an object', () => {
      const { result } = renderHook(
        () => useVocabs([{ name: 'vocab.a' }, 'not an object']),
        { wrapper },
      );
      expect(result.error).toEqual(
        new Error(
          'useVocabs: options must be an object, { name, isMultilingual } is expected [got: "not an object"]',
        ),
      );
    });

    it('should throw when an element has no name', () => {
      const { result } = renderHook(
        () => useVocabs([{ name: 'vocab.a' }, { isMultilingual: false }]),
        { wrapper },
      );
      expect(result.error).toEqual(
        new Error(
          'useVocabs: name is required [got: {"isMultilingual":false}]',
        ),
      );
    });
  });

  describe('multiple vocabs', () => {
    let mockDispatch;

    beforeEach(() => {
      jest.clearAllMocks();
      mockDispatch = jest.fn(() => Promise.resolve({ items: [] }));
      useDispatch.mockReturnValue(mockDispatch);
      store = mockStore({
        vocabularies: {},
        intl: { locale: 'en' },
      });
      isVocabRequested.mockReturnValue(false);
    });

    it('should dispatch getVocabulary for each vocab that is not loaded', async () => {
      const { rerender } = renderHook(
        () =>
          useVocabs([
            { name: 'vocab.a', isMultilingual: false },
            { name: 'vocab.b', isMultilingual: true },
          ]),
        { wrapper },
      );

      rerender();

      await waitFor(() => {
        expect(getVocabulary).toHaveBeenCalledWith({
          vocabNameOrURL: 'vocab.a',
          size: -1,
          subrequest: undefined,
        });
        expect(getVocabulary).toHaveBeenCalledWith({
          vocabNameOrURL: 'vocab.b',
          size: -1,
          subrequest: 'en',
        });
      });
    });

    it('should return items keyed by vocab name', () => {
      store = mockStore({
        vocabularies: {
          'vocab.a': { items: items1 },
          'vocab.b': { subrequests: { en: { items: items2 } } },
        },
        intl: { locale: 'en' },
      });

      const { result } = renderHook(
        () =>
          useVocabs([
            { name: 'vocab.a', isMultilingual: false },
            { name: 'vocab.b', isMultilingual: true },
          ]),
        { wrapper },
      );

      expect(result.current).toEqual({
        'vocab.a': items1,
        'vocab.b': items2,
      });
    });

    it('should not dispatch for vocabs already requested', async () => {
      isVocabRequested.mockReturnValue(true);

      renderHook(
        () =>
          useVocabs([
            { name: 'vocab.a', isMultilingual: false },
            { name: 'vocab.b', isMultilingual: true },
          ]),
        { wrapper },
      );

      expect(getVocabulary).not.toHaveBeenCalled();
    });
  });
});
