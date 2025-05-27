import pandas as pd
import re
import streamlit as st

# Load and clean data
def load_data():
    df = pd.read_excel("Updated File - 3-24.xlsx", sheet_name="Export")
    df["Normalized Haydon Part"] = df["Haydon Part #"].apply(normalize)
    return df

# Normalization function: strips spaces, dashes, asterisks, etc.
def normalize(part):
    if pd.isna(part):
        return ""
    return re.sub(r"[^A-Za-z0-9]", "", str(part)).lower()

# Search function
def search_parts(df, query):
    normalized_query = normalize(query)
    return df[df["Normalized Haydon Part"].str.contains(normalized_query, na=False)]

# Streamlit app
st.title("Haydon Cross-Reference Search")

query = st.text_input("Enter Haydon part number (or partial):")

if query:
    df = load_data()
    results = search_parts(df, query)

    if not results.empty:
        st.write(f"Found {len(results)} matching entries:")
        st.dataframe(results.drop(columns=["Normalized Haydon Part"]))
    else:
        st.warning("No matches found.")
