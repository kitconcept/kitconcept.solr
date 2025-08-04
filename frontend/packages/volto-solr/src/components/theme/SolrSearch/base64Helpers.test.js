import { aToB, bToA } from './base64Helpers';

// polyfill needed because of jsDom version used by jest
import { TextEncoder, TextDecoder } from 'util';
Object.assign(global, { TextDecoder, TextEncoder });

describe('base64helpers', () => {
  describe('bToA', () => {
    it('works', () => {
      expect(bToA('a Ā 𐀀 文 🦄')).toEqual('YSDEgCDwkICAIOaWhyDwn6aE');
    });
  });
  describe('aToB', () => {
    it('works', () => {
      expect(aToB('YSDEgCDwkICAIOaWhyDwn6aE')).toEqual('a Ā 𐀀 文 🦄');
    });
  });
});
