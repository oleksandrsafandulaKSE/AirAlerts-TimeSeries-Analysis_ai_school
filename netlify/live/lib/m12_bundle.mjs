// The M12 registry as bundled into the Netlify functions (plans/M12.md §B). activation.json decides ACTIVE; as shipped
// it is {"active": false}: the new path archives predictions only and the map keeps the M8 output.
import registry from "../model/m12/registry.json" with { type: "json" };
import activation from "../model/m12/activation.json" with { type: "json" };
import seed from "../model/m12/blend_seed.json" with { type: "json" };
import any_h1 from "../model/m12/model_any_h1.json" with { type: "json" };
import any_h3 from "../model/m12/model_any_h3.json" with { type: "json" };
import any_h6 from "../model/m12/model_any_h6.json" with { type: "json" };
import any_h12 from "../model/m12/model_any_h12.json" with { type: "json" };
import any_h24 from "../model/m12/model_any_h24.json" with { type: "json" };
import yellow_h1 from "../model/m12/model_yellow_h1.json" with { type: "json" };
import yellow_h3 from "../model/m12/model_yellow_h3.json" with { type: "json" };
import red_h1 from "../model/m12/model_red_h1.json" with { type: "json" };
import red_h3 from "../model/m12/model_red_h3.json" with { type: "json" };
import { loadRegistry } from "./models.mjs";

export const m12 = loadRegistry({ registry, activation, seed,
  models: { any_h1, any_h3, any_h6, any_h12, any_h24, yellow_h1, yellow_h3, red_h1, red_h3 } });
