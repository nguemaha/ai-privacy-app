import streamlit as st
import pandas as pd
import numpy as np
import hashlib

# --- PAGE CONFIG ---
st.set_page_config(page_title="HMA Privacy-Enhancing Toolkit", layout="wide")

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title("🛡️ HMA Clinical Data De-Identifier")
st.markdown("""
**Executive Summary:** This tool demonstrates the **HMA Lean Governance Protocol**. It transitions raw clinical data 
containing PII into a de-identified, research-ready dataset using **K-Anonymity** and **Cryptographic Hashing**.
""")

# --- 1. GENERATE SYNTHETIC "DIRTY" DATA ---
@st.cache_data
def load_synthetic_data():
    np.random.seed(42)
    data = {
        'Patient_Name': ['John Smith', 'Maria Garcia', 'Robert Chen', 'Sarah Johnson', 'Michael Brown', 
                         'Emma Wilson', 'David Miller', 'Lisa Anderson', 'James Taylor', 'Ana Martinez'],
        'Patient_ID': [f"PID-{np.random.randint(1000, 9999)}" for _ in range(10)],
        'Age': [23, 25, 31, 34, 45, 47, 52, 58, 61, 64],
        'ZIP_Code': ['12345', '12347', '12401', '12402', '54321', '54322', '90210', '90211', '33101', '33105'],
        'Gender': ['M', 'F', 'M', 'F', 'M', 'F', 'M', 'F', 'M', 'F'],
        'Diagnosis': ['Hypertension', 'Diabetes', 'Asthma', 'Hypertension', 'Diabetes', 
                      'Asthma', 'Hypertension', 'Hypertension', 'Diabetes', 'Asthma'],
        'Treatment_Cost': np.random.uniform(500, 5000, 10).round(2)
    }
    return pd.DataFrame(data)

# --- Allow user to upload CSV file ---
uploaded_file = st.sidebar.file_uploader(
    "Upload CSV with required columns (Patient_Name, Patient_ID, Age, ZIP_Code, Gender, Diagnosis, Treatment_Cost):",
    type=["csv"]
)

if uploaded_file is not None:
    try:
        raw_df = pd.read_csv(uploaded_file)
        st.sidebar.success("CSV uploaded successfully.")
    except Exception as e:
        st.sidebar.error(f"Error reading CSV: {e}")
        raw_df = load_synthetic_data()
else:
    raw_df = load_synthetic_data()

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Privacy Settings")
k_value = st.sidebar.slider("Select K-Anonymity Level (k)", 1, 5, 2)
hash_salt = st.sidebar.text_input("Encryption Salt", "HMA-2026-SECURE", type="password")

# Multiselect for Quasi-Identifiers
quasi_identifier_options = ['Age', 'ZIP_Code', 'Gender']
selected_quasi_identifiers = st.sidebar.multiselect(
    "Select Quasi-Identifiers for K-Anonymity",
    options=quasi_identifier_options,
    default=quasi_identifier_options  # All selected by default
)

st.sidebar.info(f"""
**K-Anonymity:** Ensuring that any individual in the dataset cannot be distinguished from at least **{k_value-1}** other individuals.
""")

# --- 2. THE DE-IDENTIFICATION LOGIC ---
def deidentify_data(df, k, salt, cols_to_check):
    df_clean = df.copy()
    
    # A. Masking Direct Identifiers (Hashing)
    def hash_val(val):
        return hashlib.sha256((str(val) + salt).encode()).hexdigest()[:12]
    
    df_clean['Patient_ID'] = df_clean['Patient_ID'].apply(hash_val)
    # Drop Name entirely (Full Redaction)
    df_clean = df_clean.drop(columns=['Patient_Name'])
    
    # B. Generalization (Age Bins)
    df_clean['Age'] = (df_clean['Age'] // 10 * 10).astype(str) + "s"
    
    # C. Generalization (ZIP Code Masking)
    df_clean['ZIP_Code'] = df_clean['ZIP_Code'].str[:3] + "**"
    
    # D. K-Anonymity Check (Flexible Implementation)
    if not cols_to_check:
        # If no quasi-identifiers selected, skip suppression
        df_clean['__dummy__'] = 1
        cols_to_check = ['__dummy__']
    counts = df_clean.groupby(cols_to_check)[cols_to_check[0]].transform('count')
    
    # If a row doesn't meet K, we "Suppress" it (remove it) to maintain privacy
    df_clean = df_clean[counts >= k]
    
    return df_clean, len(df) - len(df_clean)

processed_df, suppressed_count = deidentify_data(raw_df, k_value, hash_salt, selected_quasi_identifiers)

# --- 3. UI TABS ---
tab1, tab2, tab3 = st.tabs(["📊 Data Transformation", "📈 Utility Analysis", "📜 Governance Report"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Raw Clinical Data (Insecure)")
        st.caption("Contains PII and high-resolution identifiers.")
        st.dataframe(raw_df, use_container_width=True)
        st.error("⚠️ Risk: PII exposure, HIPAA non-compliance. [Learn more about HIPAA compliance](https://www.hhs.gov/hipaa/for-professionals/privacy/index.html)")

    with col2:
        st.subheader("De-identified Data (Secure)")
        st.caption(f"Applied Hashing, Generalization, and K={k_value} Anonymity.")
        st.dataframe(processed_df, use_container_width=True)
        if suppressed_count > 0:
            st.warning(f"ℹ️ {suppressed_count} rows suppressed to maintain K-Anonymity.")
        else:
            st.success("✅ Privacy requirements met for all rows.")

with tab2:
    st.subheader("Privacy vs. Utility Trade-off")
    c1, c2 = st.columns(2)
    
    # Compare Average Cost by Diagnosis (Raw vs Processed)
    raw_avg = raw_df.groupby('Diagnosis')['Treatment_Cost'].mean()
    proc_avg = processed_df.groupby('Diagnosis')['Treatment_Cost'].mean()
    
    with c1:
        st.metric("Data Retention", f"{(len(processed_df)/len(raw_df))*100:.0f}%")
        st.write("Average Cost by Diagnosis (Raw)")
        st.bar_chart(raw_avg)
        
    with c2:
        st.metric("Privacy Score", "High" if k_value > 2 else "Medium")
        st.write("Average Cost by Diagnosis (Protected)")
        st.bar_chart(proc_avg)
    
    st.info("Notice: Despite de-identification, the high-level clinical trends remain visible for research.")

with tab3:
    st.subheader("HMA Audit Log")
    st.markdown(f"""
    **Audit ID:** `SEC-DOC-{hashlib.md5(hash_salt.encode()).hexdigest()[:6].upper()}`  
    **Framework Alignment:** NIST AI RMF (Privacy-Preserving Segment)  
    
    **Transformations Applied:**
    - **SHA-256 Hashing:** Applied to `Patient_ID`.
    - **Redaction:** `Patient_Name` removed from output.
    - **Age Binning:** Generalization to decadal groups.
    - **ZIP Suppression:** Truncation of last 2 digits.
    - **K-Anonymity:** Enforced level of **{k_value}**.
    """)
    
    st.download_button(
        label="Download De-identified Dataset",
        data=processed_df.to_csv(index=False),
        file_name="hma_secure_data.csv",
        mime="text/csv"
    )

# --- FOOTER ---
st.divider()
st.caption("Developed by Healthy Moms Action (HMA) - AI Security & Governance Portfolio Case Study.")