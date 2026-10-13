// stdin: {alerts:[{unit,start,end}], taus:[ms], historyStart, gaps:[[a,b]], zones:[[a,b]]} -> stdout features + offsets
import { readFileSync } from "node:fs";
import { unitIntervals, featuresAt, offsetAt } from "../lib/features.mjs";
const regions = JSON.parse(readFileSync(new URL("../data/regions.json", import.meta.url)));
const inp = JSON.parse(readFileSync(0, "utf8"));
const res = inp.taus.map(tau => {
  const known = inp.alerts.filter(a => a.start <= tau).map(a => ({ ...a, end: a.end !== null && a.end <= tau ? a.end : null }));
  const ivs = unitIntervals(known);
  return { tau, features: featuresAt(ivs, tau, regions, inp.zones), offset: offsetAt(ivs, tau, regions, inp.historyStart, inp.gaps) };
});
process.stdout.write(JSON.stringify(res, (k, v) => (typeof v === "number" && Number.isNaN(v) ? "NaN" : v)));
