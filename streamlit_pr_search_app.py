import streamlit as st
import pandas as pd

def get_connected(df, pr):
    """Find all PR-numbers in col D/L connected to the given PR."""
    col_D = df.iloc[:, 3].astype(str)
    col_L = df.iloc[:, 11].astype(str)
    mask_D = col_D == pr
    mask_L = col_L == pr
    connected_D = set(col_L[mask_D])
    connected_L = set(col_D[mask_L])
    return sorted(x for x in (connected_D | connected_L) if x and x != pr)

def multi_level_search(df, initial_pr):
    """Run first- and second-level searches."""
    level1 = get_connected(df, initial_pr)
    level2 = {pr1: get_connected(df, pr1) for pr1 in level1}
    return level1, level2

def main():
    st.title("PR-Number Variant Management Search")
    st.markdown("""
    1. Upload an Excel file with sheet `Zwang_Ausschluss_Quelle`.  
    2. Filter by body type (column `BTYP`).  
    3. Select an initial PR to see first- and second-level connections.
    """)

    uploaded = st.file_uploader("Choose an Excel file", type=["xlsx"])
    if not uploaded:
        st.info("Please upload an Excel file.")
        return

    try:
        df = pd.read_excel(uploaded, sheet_name='Zwang_Ausschluss_Quelle')
    except Exception as e:
        st.error(f"Error loading sheet: {e}")
        return

    # --- Body-type filter ---
    if 'BTYP' not in df.columns:
        st.error("Column `BTYP` not found in the sheet.")
        return

    df['BTYP'] = df['BTYP'].astype(str)
    btypes = sorted(df['BTYP'].dropna().unique())
    selected_btyp = st.selectbox("Select Body Type", btypes)

    # apply filter
    df = df[df['BTYP'] == selected_btyp]
    st.write(f"Filtered to **{selected_btyp}**, {len(df)} rows remain.")

    # --- PR list & searches ---
    col_D_name, col_L_name = df.columns[3], df.columns[11]
    st.write(f"Using columns **{col_D_name}** (D) & **{col_L_name}** (L)")

    prs_D = df[col_D_name].dropna().astype(str)
    prs_L = df[col_L_name].dropna().astype(str)
    unique_prs = sorted(set(prs_D) | set(prs_L))

    initial_pr = st.selectbox("Select Initial PR-Number", unique_prs)
    if not initial_pr:
        return

    lvl1, lvl2 = multi_level_search(df, initial_pr)

    st.subheader("First-Level Connections")
    st.write(lvl1 or "None found.")

    st.subheader("Second-Level Connections")
    if lvl2:
        for pr1, conns in lvl2.items():
            st.write(f"From **{pr1}** → {conns or 'None.'}")
    else:
        st.write("No second-level connections (first level was empty).")

if __name__ == "__main__":
    main()
