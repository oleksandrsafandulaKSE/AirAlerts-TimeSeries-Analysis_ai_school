// stdin: {records:[{id,unit,alert_type,level,start,end}], taus:[ms], historyStart, zones:[[a,b]]} -> stdout typed output
// per tau. The state holds every record as known from its start (end known at its end time), and typed coverage
// confirmed from historyStart on, so it matches the Python truncation used by tests/test_live_typed_parity.py.
import { readFileSync } from "node:fs";
import { typedAt } from "../lib/typed.mjs";
const regions = JSON.parse(readFileSync(new URL("../data/regions.json", import.meta.url)));
const inp = JSON.parse(readFileSync(0, "utf8"));
const state = { records: {}, coverage: {}, levelCoverage: {}, polls: [], rotation: 0, historyStart: inp.historyStart,
                rejections: [], historyFail: {} };
for (const r of inp.records) state.records[r.id] = { id: r.id, unit: r.unit, level: "raion", alert_type: r.alert_type, start: r.start,
  end: r.end, updated: r.start, firstSeen: r.start, endKnown: r.end, endSource: r.end === null ? null : "history", absent: [],
  levels: [[r.start, r.level]] };
for (const u of regions.units) state.levelCoverage[u] = state.coverage[u] = [[inp.historyStart, 8.64e15, inp.historyStart]];
const out = inp.taus.map(tau => ({ tau, ...typedAt(state, tau, regions, inp.zones) }));
process.stdout.write(JSON.stringify(out));
