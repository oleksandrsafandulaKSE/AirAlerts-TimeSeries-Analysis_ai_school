### Shell: `'cat plans/M4.md'`
# M4 plan v1 — Models (H = 1, H = 3) + the single final-test scoring + new-regime section

Status: AGREED (consensus round 5, D-026; D-027 applied; history_start corrected). See reviews/M4-consensus.md. Human decisions already given in chat
(2026-10-13): one model per horizon ("option 1") → train an H = 1 model (headline) and an H = 3 model
(extra results row); the new-regime section stays H = 1 (M3b provisional decision).
Rules: CLAUDE.md, D-005, D-006, D-007, D-011, D-013, D-015 (amended by D-
### Shell: `'cat CLAUDE.md'`
# Air-raid alert forecasting — project rules for Claude Code

## Goal
Forecast, per Ukrainian oblast, the probability that a NEW air-raid alert starts in the
next H hours, given everything known at forecast time t. Evaluate on the most recent weeks
of the official dataset (which ends 2026-09-07), plus a separate exploratory check on the
new yellow/red regime (see D-007).
Deadline: Mon 12 Oct 2026, 23:59 Kyiv. Simple + correct + explained beats complex.

## The human is the architect
Oleksandr ow
### Shell: `'cat /private/tmp/claude-501/codex-artillery.md'`
# Consultation (post-consensus implementation decision, M4 §5.1) — API alert types

The human is asleep and delegated design decisions to the Claude–Codex pair ("you and codex decide what is best").
The M4 loop already used its 5 rounds; this is ONE targeted question, not a new plan round.

Facts (dump 2026-10-12T1645Z, verified by Claude's loader and independently by the reviewer subagent):
- API `alert_type` values for the 24 units: air_raid 16,448; artillery_shelling 288; urban_fights 1.
- Th
### Shell: `'cat DECISIONS.md'`
# Decisions and challenge log

Format per entry: **Context → AI proposed → I questioned/checked → Evidence → Decision**.
Mark the source honestly (builder / reviewer subagent / supervisor chat / me).

---

## D-000 — Forecast region scope and horizon
- Options: all oblasts with group reporting vs. 1–2 focus regions; H = 1h vs 3h/6h.
- Builder proposed all oblasts, H = 1 (already the CLAUDE.md default, so no extra cost).
- Decision (me, 2026-10-12): all 24 units, H = 1, one pooled model, results 
### Shell: `"sed -n '120,320p' DECISIONS.md"`
  last H hours before every cut-off.

## D-015 — What to do with the yellow zone (new-regime analysis)
- **Amended by D-021:** the (d) conclusion is conditional on the transfer results.
- Context (source: me): before Sept 2026, ANY attack (drone or missile) triggered the single
  (red) alert. Since Sept: yellow = drones, red = missiles. So "yellow or red" is the
  conceptual continuation of the old target.
- Builder found (official 27 Jul–28 Aug vs API 13 Sep–11 Oct, alerts > 24h excluded,
  ons
### Shell: `"rg -n 'alert_type|def load_api|before_after|regime_summary' src/data.py src/evaluate.py scripts/run_all.py tests/test_api_loader.py"`
src/data.py:152:    stats["non_air_raid_dropped"] = raw.loc[raw["alert_type"] != "air_raid", "alert_type"].value_counts().to_dict()
src/data.py:153:    raw = raw.loc[raw["alert_type"] == "air_raid"].copy()
src/data.py:205:def load_api(dump_dir, cfg, stats=None):
tests/test_api_loader.py:16:            "updated_at": upd or (end or start), "alert_type": kind, "alert_level": lvl,
scripts/run_all.py:495:    ba.to_csv(out_dir / "before_after.csv", index=False)

### Shell: `"rg --files -g AGENTS.md -g '*official*' -g '*api*' -g '*review*' -g '*consensus*' reviews src tests data/raw"`
tests/test_api_loader.py
reviews/M5-consensus.md
reviews/M4-consensus.md
reviews/M3b-H3-consensus.md

### Shell: `"sed -n '70,225p' src/data.py
sed -n '1,140p' tests/test_api_loader.py"`
    finished = pd.to_datetime(kept["finished_at"].replace("", None), utc=True, format="ISO8601")
    if (finished < started).any():
        raise DataQualityError(f"{int((finished < started).sum())} rows with finished_at < started_at")

    alert_id = kept.apply(lambda r: hashlib.sha1("\x1f".join(r.values).encode()).hexdigest(), axis=1)
    out = pd.DataFrame({
        "source": "official",
        "alert_id": alert_id.values,
        "unit": unit.values,
        "level": kept["level"].values,
 
I’ll read the consultation and priority files first, then check the relevant code and answer in the requested format.
**C.** A is the strongest empirical candidate: the Nikopol evidence suggests that excluding artillery would make the API target differ from the training feed. But that evidence remains an inference; the official file’s missing type column prevents confirming equivalence.

D-015’s “any alert” is explained as **yellow or red**, continuing the drone/missile target. It does not explicitly authorize artillery-shelling or urban-fighting alerts. CLAUDE.md still specifies air-raid onsets, and M4 §5.1 explicitly requires non-air-raid types to raise. The current code’s counted drop contradicts that agreed check.

Under these written rules, adopting A changes the permitted target population and its active-alert mask. **That must be treated as a rule change, which D-026 reserves for the human.** Delegating design decisions does not explicitly waive that boundary. B also cannot establish comparability merely by flagging Dnipropetrovska.

When the human returns, recommend A with per-type counts and an air-raid-only sensitivity analysis, while describing official-feed equivalence as a hypothesis.

DECISION: C
