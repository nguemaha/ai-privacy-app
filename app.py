import streamlit as st

from apps.deidentifier import render as render_deidentifier
from apps.rmf_scorecard import render as render_rmf_scorecard


def main() -> None:
    st.set_page_config(page_title="AI Privacy App", page_icon="🛡️", layout="wide")

    # Keep navigation lightweight so each page's layout stays intact,
    # but make it very visible (high-contrast "tab" buttons).
    st.markdown(
        """
<style>
  /* Reduce vertical whitespace above the selector */
  .block-container { padding-top: 1.75rem; }

  /* Header */
  .dashboard-header {
    margin-top: .25rem;
    padding: 1rem 1.1rem;
    border-radius: 16px;
    border: 1px solid rgba(0,0,0,0.08);
    background: linear-gradient(180deg, rgba(255,255,255,0.96), rgba(245,247,249,0.96));
    box-shadow: 0 10px 24px rgba(0,0,0,0.08);
    margin-bottom: .75rem;
  }
  .dashboard-title {
    margin: 0;
    font-size: 1.75rem;
    font-weight: 800;
    letter-spacing: .2px;
    line-height: 1.15;
  }
  .dashboard-subtitle {
    margin: .25rem 0 0 0;
    font-size: .98rem;
    opacity: .75;
  }

  /* Visible nav bar */
  .app-nav {
    padding: .75rem;
    border-radius: 14px;
    border: 1px solid rgba(0,0,0,0.10);
    background: rgba(255,255,255,0.92);
    box-shadow: 0 8px 20px rgba(0,0,0,0.10);
    margin-bottom: .75rem;
  }
</style>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="dashboard-header">
  <div class="dashboard-title">HMA |AI Governance and Risk Assessment Tool</div>
  <div class="dashboard-subtitle">Privacy tooling + NIST AI RMF readiness in one place.</div>
</div>
""",
        unsafe_allow_html=True,
    )

    # Page selection lives in session_state so switching is instant and stable.
    if "active_app_page" not in st.session_state:
        st.session_state.active_app_page = "deidentifier"

    with st.container():
        st.markdown("<div class='app-nav'>", unsafe_allow_html=True)
        st.markdown("**Switch tools**")
        c1, c2 = st.columns(2)
        with c1:
            if st.button(
                "🧬 HMA Clinical Data De-Identifier",
                use_container_width=True,
                type="primary"
                if st.session_state.active_app_page == "deidentifier"
                else "secondary",
            ):
                st.session_state.active_app_page = "deidentifier"
                st.rerun()
        with c2:
            if st.button(
                "🛡️ AI RMF Readiness Scorecard",
                use_container_width=True,
                type="primary"
                if st.session_state.active_app_page == "rmf"
                else "secondary",
            ):
                st.session_state.active_app_page = "rmf"
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.active_app_page == "deidentifier":
        render_deidentifier()
    else:
        render_rmf_scorecard()


if __name__ == "__main__":
    main()