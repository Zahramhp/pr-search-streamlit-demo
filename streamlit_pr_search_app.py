import streamlit as st
import pandas as pd

# Helper to clean PR-number strings

def clean_pr(s):
    """
    Remove leading apostrophes and surrounding whitespace.
    """
    return str(s).lstrip("'").strip()


def main():
    st.title("Filter Data by Body Type and List PR-Numbers")

    # 1) File upload
    uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])
    if not uploaded_file:
        st.info("Please upload an Excel file to proceed.")
        return

    # 2) Read and normalize sheet
    try:
        df = pd.read_excel(uploaded_file, sheet_name='Zwang_Ausschluss_Quelle')
    except Exception as e:
        st.error(f"Failed to read Excel file or sheet: {e}")
        return
    df.columns = [col.strip() for col in df.columns]

    # 3) Check BTYP
    if 'BTYP' not in df.columns:
        st.error(f"Column 'BTYP' not found. Available columns: {df.columns.tolist()}")
        return

    # 4) Select BTYP filter
    df['BTYP'] = df['BTYP'].astype(str)
    body_types = sorted(df['BTYP'].unique())
    options = ["-- select body type --"] + body_types
    selected_btyp = st.selectbox("Select Body Type", options)
    if selected_btyp == "-- select body type --":
        st.info("Please choose a body type above to list PR-numbers.")
        return

    # 5) Filter DataFrame by BTYP
    filtered_df = df[df['BTYP'] == selected_btyp]
    st.write(f"Filtered to **{selected_btyp}**, {len(filtered_df)} rows remain.")

    # 6) Build and clean list of unique PR-numbers from M_NR and Z_MNR
    for col in ('M_NR', 'Z_MNR'):
        if col not in filtered_df.columns:
            st.error(f"Required column '{col}' not found.")
            return

    prs_D = filtered_df['M_NR'].dropna().astype(str).map(clean_pr)
    prs_L = filtered_df['Z_MNR'].dropna().astype(str).map(clean_pr)
    prs_D = prs_D[prs_D != ""]
    prs_L = prs_L[prs_L != ""]
    unique_prs = sorted(set(prs_D) | set(prs_L))

    # 7) Tabbed display for PR list and selection
    tab_list, tab_select = st.tabs(["PR List", "Select PR"])
    with tab_list:
        st.subheader("Available PR-Numbers")
        st.write(unique_prs)

    with tab_select:
        st.subheader("Choose an Initial PR-Number")
        selected_pr = st.selectbox("Select PR-Number", unique_prs)
        if not selected_pr:
            return
        st.write(f"You selected: **{selected_pr}**")

        # 8) Filtered DataFrames based on selected PR
        # Rows where M_NR matches
        df_mnr = filtered_df[filtered_df['M_NR'].astype(str).map(clean_pr) == selected_pr]
        # Rows where Z_MNR matches
        df_zmnr = filtered_df[filtered_df['Z_MNR'].astype(str).map(clean_pr) == selected_pr]

        st.subheader("Filtered by M_NR")
        st.dataframe(df_mnr)

        st.subheader("Filtered by Z_MNR")
        st.dataframe(df_zmnr)

if __name__ == "__main__":
    main()
