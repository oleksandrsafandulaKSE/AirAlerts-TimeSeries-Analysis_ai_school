# M6-site — reviewer subagent + harness review (after implementation)

## Reviewer (ML validity): FIX FIRST → fixed
No leakage found. Golden "any" re-derived from git HEAD independently (192 unit-forecasts, identical). 8 of 10 one-line
mutations caught by typed.test.mjs.
1. (medium) rejected ACTIVE record left typed as forecast → FIXED (typed data gap + test).
2. (medium) a typed error could take down the "any" forecast / the GET → FIXED (contained, reported in payload + status; tests).
3. (low/medium) a level changed in place by the API revises past typed labels. Checked the datastore: 3 of 20,270 ids
   changed level (red → yellow, Kharkivska, 12 Oct). KEPT: follows CLAUDE.md's API merge rule (latest updated_at), as
   known at τ — never a leak. Question for the human.
4. (low) firstSeen filter not caught → FIXED (witness (d) in the truncation test). trained_through > τ check is
   unreachable after selectModel; kept as a defensive check.
5. (low) wording "same 60 minutes" → "next"; "N days in total" → FIXED.
6. (low) `.claude/launch.json` deleted by me (overwritten by a scratch mock config, then removed) → RESTORED from git.
   Seed not rebuilt → stated in the summary (the gitignored seed lives in the main checkout; the human rebuilds it).

## Harness review (ran the code): 4 findings → 3 fixed
1. (medium) `levels` grew on duplicate ids / flapping level with the same updated_at → FIXED (strictly newer only; test).
2. (low) typed baseline can be exactly 0 → DOCUMENTED: q = 0 for a unit that has never had that level, identical to
   improve/live_ref.py (parity); the page shows "<1%".
3. (low) page functions printed NaN/undefined on partial fields → FIXED (guards + test).
4. (low) old-format seed → as reviewer 6; the migration recovers in ~24 min (history_days 29 → 34).
Worked fine: old-store start, "any" replay vs HEAD (300 runs, 0 diffs), serialisation, payload ~13.7 KB, escaping,
circular import, function JSON import, typed errors contained.
