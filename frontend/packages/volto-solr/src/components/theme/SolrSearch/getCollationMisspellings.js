export const getCollationMisspellings = (collationMisspellings) =>
  Object.fromEntries(
    Array.from(
      { length: Math.floor((collationMisspellings?.length ?? 0) / 2) },
      (_, i) => collationMisspellings.slice(i * 2, i * 2 + 2),
    ),
  );
