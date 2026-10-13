import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { rawScore, predictOffset, logit } from "../lib/lgb.mjs";

const dir = new URL("../model/", import.meta.url);
const model = JSON.parse(readFileSync(new URL("model_live.json", dir)));
const sample = JSON.parse(readFileSync(new URL("parity_sample.json", dir)));

test("JS tree evaluation equals LightGBM raw scores and probabilities", () => {
  let maxRaw = 0, maxP = 0;
  for (const r of sample.rows) {
    maxRaw = Math.max(maxRaw, Math.abs(rawScore(model, r.x) - r.raw));
    maxP = Math.max(maxP, Math.abs(predictOffset(model, r.x, r.offset_rate) - r.p));
  }
  assert.ok(maxRaw < 1e-9, `max raw diff ${maxRaw}`);
  assert.ok(maxP < 1e-9, `max p diff ${maxP}`);
  assert.equal(sample.rows.length, 5000);
});

test("feature order matches the model", () => {
  assert.deepEqual(model.feature_names, sample.features);
});

test("categorical unit_code split and invalid offsets", () => {
  const cat = JSON.stringify(model).includes('"decision_type":"=="');
  assert.ok(cat, "the dump should contain a categorical split on unit_code");
  assert.throws(() => logit(1.5));
  assert.throws(() => logit(NaN));
  assert.equal(Math.round(1 / (1 + Math.exp(-logit(0))) * 1e6) / 1e6, 1e-4);
});
