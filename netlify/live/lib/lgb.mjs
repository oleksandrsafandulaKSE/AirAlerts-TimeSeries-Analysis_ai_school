// Evaluate a LightGBM `dump_model()` tree ensemble in JavaScript (plans/M8.md §2).
// Numerical splits ("<="), categorical splits ("==", categories "a||b"), missing handling (None / Zero / NaN).

function goLeft(node, v) {
  const missingType = node.missing_type;
  if (node.decision_type === "==") {
    if (v === null || Number.isNaN(v) || v < 0) return false;          // missing / invalid category -> right
    const cats = String(node.threshold).split("||").map(Number);
    return cats.includes(Math.trunc(v));
  }
  let x = v;
  if (x === null || Number.isNaN(x)) {
    if (missingType === "NaN") return node.default_left;
    x = 0;                                                             // "None": NaN treated as 0
  }
  if (missingType === "Zero" && x === 0) return node.default_left;
  return x <= node.threshold;
}

export function treeValue(node, x) {
  while (node.leaf_value === undefined) {
    node = goLeft(node, x[node.split_feature]) ? node.left_child : node.right_child;
  }
  return node.leaf_value;
}

export function rawScore(model, x) {
  let s = 0;
  for (const t of model.tree_info) s += treeValue(t.tree_structure, x);
  return s;
}

export const CLIP = 1e-4;

export function logit(rate) {
  if (rate === null || Number.isNaN(rate) || rate < 0 || rate > 1) throw new Error("offset rate must be in [0, 1]");
  const r = Math.min(Math.max(rate, CLIP), 1 - CLIP);
  return Math.log(r / (1 - r));
}

export function predictOffset(model, x, offsetRate) {
  const z = logit(offsetRate) + rawScore(model, x);
  return 1 / (1 + Math.exp(-z));
}
