# app.py
# Streamlit app: NIST AI RMF Readiness Scorecard (40 questions)
# Run: streamlit run app.py

import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="AI RMF Readiness Scorecard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Styling (simple, clean, "dashboard-y") ----------
st.markdown(
    """
    <style>
      .block-container { padding-top: 1.2rem; padding-bottom: 2rem; }
      .score-card {
        padding: 1rem 1.1rem; border-radius: 16px; border: 1px solid rgba(255,255,255,0.10);
        background: linear-gradient(135deg, rgba(255,255,255,0.07), rgba(255,255,255,0.03));
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
      }
      .dim-title { font-size: 1.05rem; font-weight: 700; margin-bottom: .25rem; }
      .muted { opacity: 0.75; font-size: 0.9rem; }
      .pill {
        display: inline-block; padding: .25rem .6rem; border-radius: 999px;
        border: 1px solid rgba(255,255,255,0.12); background: rgba(255,255,255,0.06);
        font-size: 0.85rem;
      }
      hr { border-top: 1px solid rgba(255,255,255,0.12); }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Question Bank (10 per dimension) ----------
QUESTIONS = {
    "GOVERN": [
        "Use-case owner: Named accountable business/clinical owner (name + role).",
        "Technical owner: Named technical owner (MLOps/data science/vendor contact).",
        "Decision authority: Defined approver/committee for go-live (e.g., governance board, CMIO, compliance).",
        "Policy alignment: Mapped applicable policies (privacy, security, CDS, procurement, IRB, etc.).",
        "Vendor accountability (if applicable): Contract includes SLAs/audit rights/change notification/incident reporting.",
        "Risk classification: Use case categorized (clinical vs operational vs patient-facing) with required rigor defined.",
        "Human oversight: Defined who can override, escalation path, and responsibilities.",
        "Training & SOPs: End-user training plan and SOPs created/approved.",
        "Audit trail: Logging/audit approach defined for outputs, decisions, and access.",
        "Go-live criteria: Explicit acceptance criteria defined (performance, safety, workflow readiness).",
    ],
    "MAP": [
        "Intended use: Clearly defined purpose and success criteria.",
        "Out of scope: Contraindicated / not-intended uses explicitly documented.",
        "Population: Target patient population and exclusions defined.",
        "Stakeholders: Impacted stakeholders identified (patients, clinicians, operations, etc.).",
        "Workflow integration: Exact integration point and downstream action defined.",
        "Consequence of error: Clinical/operational consequences documented (severity + context).",
        "Risk/harm analysis: Structured harm analysis performed (e.g., failure modes + mitigations).",
        "Equity considerations: Potential differential impacts across subgroups assessed.",
        "Data provenance: Data sources and known quality gaps documented.",
        "Assumptions & constraints: Key assumptions/constraints documented (availability, timing, dependencies).",
    ],
    "MEASURE": [
        "Local validation: Validated on your setting/data (not only vendor/paper results).",
        "Performance metrics: Metrics defined and reported; threshold rationale documented.",
        "Calibration: Calibration assessed and acceptable for intended decision-making.",
        "Subgroup performance: Evaluated across key subgroups relevant to the use case.",
        "Drift sensitivity: Drift risk assessed (documentation/coding/workflow changes).",
        "Robustness tests: Tested under missing data, edge cases, downtime/latency scenarios.",
        "Explainability: Explanation method suitable for end users and governance review.",
        "Privacy review: PHI use assessed; minimization/retention/consent decisions documented.",
        "Security review: Security threats assessed (access controls, prompt injection for LLMs, model inversion, etc.).",
        "Monitoring signals: Defined what metrics/signals will be monitored post-go-live.",
    ],
    "MANAGE": [
        "Deployment plan: Rollout approach defined (pilot/phased) with responsible parties.",
        "Rollback plan: Fast disable/rollback procedure documented and tested (where feasible).",
        "Alert fatigue controls: Controls defined (rate limits, prioritization, suppression rules).",
        "Monitoring ownership: Who reviews dashboards, how often, and SLAs for investigation defined.",
        "Incident response: AI incident playbook defined (triage, reporting, escalation).",
        "Change management: Re-validation triggers defined (EHR upgrades, pathway changes, new devices).",
        "Versioning & documentation: Model versions tracked and tied to eval artifacts.",
        "Retraining policy: If retraining occurs, approval/testing steps defined.",
        "Feedback loop: End-user feedback mechanism exists and is routed for review.",
        "Post-implementation review: Scheduled 30/60/90-day review with outcomes/unintended effects.",
    ],
}

DIM_ORDER = ["GOVERN", "MAP", "MEASURE", "MANAGE"]

# ---------- Helpers ----------
def init_state():
    for dim in DIM_ORDER:
        for i in range(len(QUESTIONS[dim])):
            k = f"{dim}_{i}"
            if k not in st.session_state:
                st.session_state[k] = False

def compute_scores():
    scores = {}
    missing = {}
    for dim in DIM_ORDER:
        vals = [1 if st.session_state[f"{dim}_{i}"] else 0 for i in range(10)]
        scores[dim] = int(round(100 * sum(vals) / 10))
        missing[dim] = [QUESTIONS[dim][i] for i, v in enumerate(vals) if v == 0]
    overall = int(round(sum(scores.values()) / len(scores)))
    return scores, missing, overall

def dim_badge(score):
    if score >= 85:
        return "✅ Strong"
    if score >= 60:
        return "🟡 Moderate"
    return "🔴 Needs work"

def reset_all():
    for dim in DIM_ORDER:
        for i in range(10):
            st.session_state[f"{dim}_{i}"] = False

# ---------- App ----------
init_state()

with st.sidebar:
    st.markdown("## 🧭 Assessment Inputs")
    st.caption("Answer the 40 controls (Yes/No). Each **Yes = 1 point**, **No = 0 points**.")
    st.markdown("---")

    # Optional metadata (not scored)
    st.markdown("### Context (optional)")
    use_case = st.text_input("AI use case / system name", placeholder="e.g., Sepsis alert model, Scheduling optimizer, LLM triage bot")
    risk_tier = st.selectbox("Risk tier", ["Unspecified", "Low", "Medium", "High"], index=0)
    st.markdown("---")

    st.markdown("### Controls (40)")
    for dim in DIM_ORDER:
        with st.expander(f"{dim} (10)", expanded=(dim == "GOVERN")):
            for i, q in enumerate(QUESTIONS[dim]):
                st.checkbox(q, key=f"{dim}_{i}")

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔄 Reset", use_container_width=True):
            reset_all()
            st.rerun()
    with c2:
        st.download_button(
            "⬇️ Export (JSON)",
            data=str({k: bool(v) for k, v in st.session_state.items() if any(k.startswith(d) for d in DIM_ORDER)}),
            file_name="ai_rmf_scorecard_responses.json",
            use_container_width=True,
        )

scores, missing, overall = compute_scores()

# ---------- Main layout ----------
st.markdown("## 🛡️ AI RMF Readiness Scorecard")
subtitle = f"<span class='pill'>Overall Score: <b>{overall}/100</b></span>  &nbsp; <span class='pill'>Generated: <b>{datetime.now().strftime('%Y-%m-%d %H:%M')}</b></span>"
if use_case.strip():
    subtitle += f" &nbsp; <span class='pill'>Use case: <b>{use_case}</b></span>"
if risk_tier != "Unspecified":
    subtitle += f" &nbsp; <span class='pill'>Risk tier: <b>{risk_tier}</b></span>"
st.markdown(subtitle, unsafe_allow_html=True)

st.markdown("---")

# Score cards + progress bars
cols = st.columns(4)
for idx, dim in enumerate(DIM_ORDER):
    with cols[idx]:
        st.markdown("<div class='score-card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='dim-title'>{dim}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='muted'>{dim_badge(scores[dim])}</div>", unsafe_allow_html=True)
        st.progress(scores[dim] / 100.0)
        st.markdown(f"**{scores[dim]} / 100**")
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("### 📌 Suggestions for improvement")
st.caption("These are the *highest-leverage* items to complete next (all currently scored 0).")

# Build a ranked action list (simple: show dim with lowest score first, then list missing)
ranked_dims = sorted(DIM_ORDER, key=lambda d: scores[d])

# Provide a concise "next actions" view
for dim in ranked_dims:
    miss = missing[dim]
    if not miss:
        continue
    with st.expander(f"{dim} — {len(miss)} missing controls (Score {scores[dim]}/100)", expanded=(dim == ranked_dims[0])):
        # Show top 5 first; rest collapses nicely inside expander anyway
        for j, item in enumerate(miss, start=1):
            st.markdown(f"{j}. {item}")

if all(len(missing[d]) == 0 for d in DIM_ORDER):
    st.success("Nice — all controls are marked complete. Your Readiness Score is 100/100.")

st.markdown("---")

# Optional: quick narrative summary
st.markdown("### 🧠 Summary narrative (auto-generated)")
lowest = ranked_dims[0]
highest = ranked_dims[-1]
summary_lines = []
summary_lines.append(f"- Your strongest area is **{highest}** at **{scores[highest]}/100**.")
summary_lines.append(f"- Your biggest opportunity is **{lowest}** at **{scores[lowest]}/100**.")
if missing[lowest]:
    summary_lines.append(f"- Next best step: complete the top missing items in **{lowest}** to lift your overall posture quickly.")
st.markdown("\n".join(summary_lines))

st.caption("Tip: Keep the sidebar as the single input surface; treat the main panel as the executive dashboard + prioritized roadmap.")
