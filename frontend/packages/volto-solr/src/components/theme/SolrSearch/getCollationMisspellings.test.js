import { getCollationMisspellings } from './getCollationMisspellings';

describe('getCollationMisspellings', () => {
  it('should return empty object for empty/null/undefined input', () => {
    expect(getCollationMisspellings([])).toEqual({});
    expect(getCollationMisspellings(null)).toEqual({});
    expect(getCollationMisspellings(undefined)).toEqual({});
  });

  it('should handle single misspelling pair', () => {
    const input = ['color', 'colour'];
    expect(getCollationMisspellings(input)).toEqual({
      color: 'colour',
    });
  });

  it('should handle multiple misspelling pairs', () => {
    const input = ['color', 'colour', 'behavior', 'behaviour'];
    expect(getCollationMisspellings(input)).toEqual({
      color: 'colour',
      behavior: 'behaviour',
    });
  });

  it('should ignore last element when array length is odd', () => {
    const input = ['color', 'colour', 'behavior'];
    expect(getCollationMisspellings(input)).toEqual({
      color: 'colour',
    });
  });
});
