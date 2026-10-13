"""Local results viewer (M5, ROADMAP/D-012). Reads ONLY saved files in reports/; no data, no model fitting, no API.

    streamlit run app/streamlit_app.py
"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
FILES = {
    "official": ["metrics.csv", "metrics_validation.csv", "calibration_in_the_large.csv", "reliability.png",
                 "reliability_validation.png", "preregistration.json", "final_test_checks.json"],
    "official_h3": ["metrics.csv", "metrics_validation.csv", "calibration_in_the_large.csv", "reliability.png",
                    "reliability_validation.png", "preregistration.json", "final_test_checks.json"],
    "new_regime": ["metrics.csv", "transfer.csv", "before_after.csv", "reliability.png", "run_meta.json"],
    "new_regime_all_types": ["metrics.csv", "transfer.csv", "before_after.csv", "reliability.png", "run_meta.json"],
}
COLS = ["baseline", "group", "rows", "base_rate", "brier", "brier_skill_vs_recent", "roc_auc_pooled",
        "roc_auc_within_unit_mean", "within_unit_units_used", "pr_auc", "pr_auc_over_base", "low_n"]


def expected_files(reports=REPORTS):
    return [Path(reports) / run / f for run, fs in FILES.items() for f in fs]


def missing_files(reports=REPORTS):
    return [p for p in expected_files(reports) if not p.exists()]


def load(reports=REPORTS):
    reports = Path(reports)
    out = {}
    for run, fs in FILES.items():
        out[run] = {}
        for f in fs:
            p = reports / run / f
            if f.endswith(".csv"):
                out[run][f] = pd.read_csv(p)
            elif f.endswith(".json"):
                out[run][f] = json.loads(p.read_text())
            else:
                out[run][f] = p
    return out


def main():
    import streamlit as st
    st.set_page_config(page_title="Air-raid onset forecasts", layout="wide")
    st.title("Air-raid alert onset forecasts — saved results")
    miss = missing_files()
    if miss:
        st.error("Missing report files (run the pipeline stages first):\n" + "\n".join(map(str, miss)))
        st.stop()
    r = load()
    st.caption("Every number below is read from reports/ written by scripts/run_all.py. The final test was scored once.")
    tab1, tab3, tabn = st.tabs(["Final test, H = 1 (headline)", "Final test, H = 3", "New alert system (exploratory)"])
    for tab, run in ((tab1, "official"), (tab3, "official_h3")):
        with tab:
            m = r[run]["metrics.csv"]
            st.subheader("Model vs baselines (primary: Brier skill vs the rolling recent rate)")
            st.dataframe(m[[c for c in COLS if c in m.columns]], hide_index=True)
            st.image(str(r[run]["reliability.png"]), caption="Reliability on the final test")
            st.subheader("Calibration-in-the-large")
            st.dataframe(r[run]["calibration_in_the_large.csv"], hide_index=True)
            with st.expander("Validation (known before the test was scored)"):
                v = r[run]["metrics_validation.csv"]
                st.dataframe(v[[c for c in COLS if c in v.columns]], hide_index=True)
                st.image(str(r[run]["reliability_validation.png"]))
            with st.expander("Pre-registration"):
                st.json(r[run]["preregistration.json"])
    with tabn:
        st.warning("Exploratory: a different data source (alerts.in.ua) and one month of history; never mixed with "
                   "the official data. The model was not retrained or tuned on it.")
        st.info("Open decision for the project owner: whether artillery-shelling alerts count. Both variants are shown.")
        variant = st.radio("Alerts counted", ["new_regime", "new_regime_all_types"],
                           format_func=lambda v: "Air-raid only" if v == "new_regime" else "All alert types")
        st.subheader("Transfer of the frozen H = 1 model")
        st.dataframe(r[variant]["transfer.csv"], hide_index=True)
        st.subheader("Before / after (onsets per 30 days, share of time under alert)")
        st.dataframe(r[variant]["before_after.csv"], hide_index=True)
        st.image(str(r[variant]["reliability.png"]))


if __name__ == "__main__":
    main()
