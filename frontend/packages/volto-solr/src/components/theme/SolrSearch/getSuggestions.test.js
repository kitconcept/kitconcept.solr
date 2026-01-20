import { getSuggestions } from './getSuggestions';

describe('getSuggestions', () => {
  it('should return empty array for empty input', () => {
    expect(getSuggestions([])).toEqual([]);
  });

  it('works', () => {
    const input = [
      'ba',
      {
        suggestion: [
          { freq: 1, word: 'bar' },
          { freq: 1, word: 'banana' },
        ],
      },
      'ap',
      {
        suggestion: [
          { freq: 1, word: 'api' },
          { freq: 1, word: 'apple' },
        ],
      },
    ];
    expect(getSuggestions(input)).toEqual(['api', 'apple', 'banana', 'bar']);
  });

  it('sorted by default freq', () => {
    const input = [
      'ba',
      {
        suggestion: [
          { freq: 1, word: 'bar' },
          { freq: 2, word: 'banana' },
        ],
      },
      'ap',
      {
        suggestion: [
          { freq: 1, word: 'api' },
          { freq: 3, word: 'apple' },
        ],
      },
    ];
    expect(getSuggestions(input)).toEqual(['apple', 'banana', 'api', 'bar']);
  });

  it('sorted by custom function', () => {
    const input = [
      'ba',
      {
        suggestion: [
          { freq: 1, word: 'bar' },
          { freq: 2, word: 'banana' },
        ],
      },
      'ap',
      {
        suggestion: [
          { freq: 1, word: 'api' },
          { freq: 3, word: 'apple' },
        ],
      },
    ];
    expect(getSuggestions(input)).toEqual(['apple', 'banana', 'api', 'bar']);
  });

  it('custom sorter function', () => {
    const input = [
      'ba',
      {
        suggestion: [
          { customfreq: 1, word: 'bar' },
          { customfreq: 2, word: 'banana' },
        ],
      },
      'ap',
      {
        suggestion: [
          { customfreq: 1, word: 'api' },
          { customfreq: 3, word: 'apple' },
        ],
      },
    ];
    expect(
      getSuggestions(input, { sorter: (a, b) => b.customfreq - a.customfreq }),
    ).toEqual(['apple', 'banana', 'api', 'bar']);
  });

  it('custom getter option', () => {
    const input = [
      'ba',
      {
        suggestion: [
          { freq: 1, customword: 'bar' },
          { freq: 1, customword: 'banana' },
        ],
      },
      'ap',
      {
        suggestion: [
          { freq: 1, customword: 'api' },
          { freq: 1, customword: 'apple' },
        ],
      },
    ];
    expect(getSuggestions(input, { getter: (i) => i.customword })).toEqual([
      'api',
      'apple',
      'banana',
      'bar',
    ]);
  });

  it('getter returns undefined', () => {
    const input = [
      'ba',
      {
        suggestion: [{ freq: 1 }, { freq: 2 }],
      },
      'ap',
      {
        suggestion: [
          { freq: 1, word: 'api' },
          { freq: 3, word: 'apple' },
        ],
      },
    ];
    expect(getSuggestions(input)).toEqual(['apple', 'api']);
  });

  it('maxLength option', () => {
    const input = [
      'ba',
      {
        suggestion: [
          { freq: 1, word: 'bar' },
          { freq: 1, word: 'banana' },
        ],
      },
      'ap',
      {
        suggestion: [
          { freq: 1, word: 'api' },
          { freq: 1, word: 'apple' },
        ],
      },
    ];
    expect(getSuggestions(input, { maxLength: 5 })).toEqual([
      'api',
      'apple',
      'banana',
      'bar',
    ]);
    expect(getSuggestions(input, { maxLength: 4 })).toEqual([
      'api',
      'apple',
      'banana',
      'bar',
    ]);
    expect(getSuggestions(input, { maxLength: 3 })).toEqual([
      'api',
      'apple',
      'banana',
    ]);
    expect(getSuggestions(input, { maxLength: 2 })).toEqual(['api', 'apple']);
    expect(getSuggestions(input, { maxLength: 1 })).toEqual(['api']);
  });

  it('removes duplicates', () => {
    const input = [
      'ba',
      {
        suggestion: [
          { freq: 1, word: 'bar' },
          { freq: 1, word: 'banana' },
        ],
      },
      'ap',
      {
        suggestion: [
          { freq: 1, word: 'api' },
          { freq: 1, word: 'apple' },
          { freq: 1, word: 'bar' },
          { freq: 1, word: 'api' },
        ],
      },
    ];
    expect(getSuggestions(input)).toEqual(['api', 'apple', 'banana', 'bar']);
  });

  it('empty', () => {
    const input = [
      'ba',
      {
        suggestion: [
          { freq: 1, word: 'bar' },
          { freq: 1, word: 'banana' },
        ],
      },
      'ap',
      { suggestion: [] },
    ];
    expect(getSuggestions(input)).toEqual(['banana', 'bar']);
  });
});
