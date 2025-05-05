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
    # Exclude empty and the original PR itself
    return sorted(x for x in (connected_D | connected_L) if x and x != pr)

def multi_level_search(df, initial_pr):
    """Run first- and second-level searches."""
    level1 = get_connected(df, initial_pr)
    level2 = {pr1: get_connected(df, pr1) for pr1 in level1}
    return level1, level2

def main():
    st.title("PR-Number Variant Management Search")
    st.markdown("""
    Upload an Excel file with sheet `Zwang_Ausschluss_Quelle` and PR-numbers in columns D & L.
    Select an initial PR to see first- and second-level connections.
    """)
    uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx"])
    if not uploaded_file:
        st.info("Please upload an Excel file.")
        return

    try:
        df = pd.read_excel(uploaded_file, sheet_name='Zwang_Ausschluss_Quelle')
        col_D_name, col_L_name = df.columns[3], df.columns[11]
        st.write(f"Using columns **{col_D_name}** (D) & **{col_L_name}** (L)")

        # Build the master list of PR-numbers
        prs_D = df[col_D_name].dropna().astype(str)
        prs_L = df[col_L_name].dropna().astype(str)
        unique_prs = sorted(set(prs_D) | set(prs_L))

        initial_pr = st.selectbox("Select Initial PR-Number", unique_prs)
        if initial_pr:
            lvl1, lvl2 = multi_level_search(df, initial_pr)

            st.subheader("First-Level Connections")
            st.write(lvl1 or "None found.")

            st.subheader("Second-Level Connections")
            if lvl2:
                for pr1, conns in lvl2.items():
                    st.write(f"From **{pr1}** → {conns or 'None.'}")
            else:
                st.write("No second-level connections (first level was empty).")

    except Exception as e:
        st.error(f"Error reading/processing file: {e}")

if __name__ == "__main__":
    main()
