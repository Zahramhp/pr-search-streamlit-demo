import streamlit as st
import pandas as pd

def get_connected(df, pr):
    col_D = df['M_NR'].astype(str)
    col_L = df['Z_MNR'].astype(str)
    return sorted(
        x for x in set(col_L[col_D == pr]) | set(col_D[col_L == pr])
        if x and x != pr
    )

def multi_level_search(df, initial_pr):
    lvl1 = get_connected(df, initial_pr)
    lvl2 = {p: get_connected(df, p) for p in lvl1}
    return lvl1, lvl2

def main():
    st.title("PR-Number Variant Management Search")

    uploaded = st.file_uploader("Upload Excel (sheet ‘Zwang_Ausschluss_Quelle’)", type=["xlsx"])
    if not uploaded:
        st.info("Please upload an Excel file.")
        return

    # 1) Load & normalize
    df = pd.read_excel(uploaded, sheet_name='Zwang_Ausschluss_Quelle')
    df.columns = [c.strip() for c in df.columns]

    # 2) Check for required cols
    for req in ('BTYP','M_NR','Z_MNR'):
        if req not in df.columns:
            st.error(f"Missing column: {req}")
            return

    # 3) Filter by body type
    df['BTYP'] = df['BTYP'].astype(str)
    btypes = sorted(df['BTYP'].dropna().unique())
    selected_btyp = st.selectbox("Select Body Type", btypes)
    df = df[df['BTYP'] == selected_btyp]
    st.write(f"Filtered to **{selected_btyp}** → {len(df)} rows")

    # 4) **Build initial list only from filtered rows**
    prs_D = df['M_NR'].dropna().astype(str)
    prs_L = df['Z_MNR'].dropna().astype(str)
    unique_prs = sorted(set(prs_D) | set(prs_L))

    initial_pr = st.selectbox("Select Initial PR-Number", unique_prs)
    if not initial_pr:
        return

    # 5) Run first & second level
    lvl1, lvl2 = multi_level_search(df, initial_pr)

    st.subheader("First-Level Connections")
    st.write(lvl1 or "None found.")

    st.subheader("Second-Level Connections")
    if lvl2:
        for p, conns in lvl2.items():
            st.write(f"From **{p}** → {conns or 'None.'}")
    else:
        st.write("No second-level connections.")

if __name__ == "__main__":
    main()
