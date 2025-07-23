import {
  encodeConditionTree,
  decodeConditionTree,
  pruneConditionTree,
} from './SearchConditions';
import { bToA } from './base64Helpers';

// polyfill needed because of jsDom version used by jest
import { TextEncoder, TextDecoder } from 'util';
Object.assign(global, { TextDecoder, TextEncoder });

describe('SOLR SearchConditions', () => {
  describe('encodeConditionTree', () => {
    it('works', () => {
      expect(encodeConditionTree({ foo: true })).toEqual(bToA('{"foo":true}'));
    });
    it('empty gives empty string', () => {
      expect(encodeConditionTree({})).toEqual('');
    });
    it('utf', () => {
      // it's important that the binary conversion works with utf,
      // as standard btoa / atob does not, and would give error
      // for accented characters when converted back from python.
      expect(encodeConditionTree({ foo: 'Atommüll' })).toEqual(
        'eyJmb28iOiJBdG9tbcO8bGwifQ==',
      );
    });
    it('utf and back', () => {
      expect(encodeConditionTree({ foo: 'Atommüll' })).toEqual(
        bToA('{"foo":"Atommüll"}'),
      );
    });
  });
  describe('decodeConditionTree', () => {
    beforeEach(() => {
      jest.spyOn(console, 'warn').mockImplementation(jest.fn());
    });
    afterEach(() => {
      // eslint-disable-next-line no-console
      console.warn.mockRestore();
    });
    it('works', () => {
      expect(decodeConditionTree(bToA('{"foo":true}'))).toEqual({ foo: true });
    });
    it('undefined gives empty', () => {
      expect(decodeConditionTree(undefined)).toEqual({});
    });
    it('empty string gives empty', () => {
      expect(decodeConditionTree('')).toEqual({});
    });
    it('errors', () => {
      expect(() => decodeConditionTree('BORKEN')).toThrow();
    });
    it('errors with {catchError: false}', () => {
      expect(() =>
        decodeConditionTree('BORKEN', { catchError: false }),
      ).toThrow();
    });
    it('errors are ignored with {catchError: true}', () => {
      expect(decodeConditionTree('BORKEN', { catchError: true })).toEqual({});
      // eslint-disable-next-line no-console
      expect(console.warn.mock.calls).toHaveLength(1);
    });
  });
  describe('pruneConditionTree', () => {
    it('works', () => {
      expect(
        pruneConditionTree({
          foo: { c: { v1: true, v2: false }, p: 'pref1', m: true },
          bar: { c: { v3: true, v4: false }, p: '', m: false },
        }),
      ).toEqual({
        foo: { c: { v1: true }, p: 'pref1', m: true },
        bar: { c: { v3: true } },
      });
    });
    it('works with empty conditions', () => {
      expect(
        pruneConditionTree({
          foo: { p: 'pref1', m: true },
          bar: { p: '', m: false },
        }),
      ).toEqual({
        foo: { p: 'pref1', m: true },
      });
    });
    it('accepts default fields', () => {
      expect(
        pruneConditionTree({
          foo: { c: { v1: true, v2: true } },
          baz: { c: {}, p: '', v: false },
        }),
      ).toEqual({ foo: { c: { v1: true, v2: true } } });
    });
    it('accepts empty fields', () => {
      expect(
        pruneConditionTree({
          foo: { c: { v1: true, v2: true } },
          baz: {},
        }),
      ).toEqual({ foo: { c: { v1: true, v2: true } } });
    });
    it('prunes default fields', () => {
      expect(
        pruneConditionTree({
          foo: { c: { v1: true, v2: true } },
          baz: { c: {}, p: '', v: false },
        }),
      ).toEqual({ foo: { c: { v1: true, v2: true } } });
    });
    it('prunes empty fields', () => {
      expect(
        pruneConditionTree({
          foo: { c: { v1: true, v2: true } },
          baz: { c: { v1: false } },
        }),
      ).toEqual({ foo: { c: { v1: true, v2: true } } });
    });
    it('prunes empty fields without default', () => {
      expect(
        pruneConditionTree({
          foo: { c: { v1: true, v2: true } },
          baz: {},
        }),
      ).toEqual({ foo: { c: { v1: true, v2: true } } });
    });
  });
});
