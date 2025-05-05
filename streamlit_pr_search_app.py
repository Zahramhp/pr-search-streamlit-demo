import streamlit as st
import pandas as pd

def main():
    st.title("Filter Data by Body Type")

    uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])
    if not uploaded_file:
        st.info("Please upload an Excel file to proceed.")
        return

    try:
        df = pd.read_excel(uploaded_file, sheet_name='Zwang_Ausschluss_Quelle')
    except Exception as e:
        st.error(f"Failed to read Excel file or sheet: {e}")
        return

    # Normalize header names
    df.columns = [col.strip() for col in df.columns]

    # Check for BTYP column
    if 'BTYP' not in df.columns:
        st.error(f"Column 'BTYP' not found. Available columns: {df.columns.tolist()}")
        return

    # Convert BTYP to string and get unique values
    df['BTYP'] = df['BTYP'].astype(str)
    body_types = sorted(df['BTYP'].unique())
    selected_btyp = st.selectbox("Select Body Type", body_types)

    # Filter by selected body type
    filtered_df = df[df['BTYP'] == selected_btyp]
    st.write(f"Showing {len(filtered_df)} rows for body type: {selected_btyp}")

    # Display filtered dataframe
    st.dataframe(filtered_df)

if __name__ == "__main__":
    main()
