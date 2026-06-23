// Serialize a chart-driven filter object to/from URL search params so that
// clicking a chart produces a shareable, refresh-safe /candidates?... link.

const KEYS = [
  "label",
  "skill",
  "trap",
  "min_score",
  "max_score",
  "min_experience",
  "max_experience",
];

export function filterToParams(filter) {
  const params = new URLSearchParams();
  if (!filter) return params;
  for (const k of KEYS) {
    if (filter[k] !== undefined && filter[k] !== null && filter[k] !== "") {
      params.set(k, String(filter[k]));
    }
  }
  return params;
}

export function paramsToFilter(searchParams) {
  const filter = {};
  let has = false;
  for (const k of KEYS) {
    const v = searchParams.get(k);
    if (v === null) continue;
    has = true;
    if (k === "label" || k === "skill" || k === "trap") {
      filter[k] = v;
    } else {
      const n = Number(v);
      filter[k] = Number.isNaN(n) ? v : n;
    }
  }
  if (!has) return null;
  if (!filter.label) filter.label = "Filtered";
  return filter;
}
