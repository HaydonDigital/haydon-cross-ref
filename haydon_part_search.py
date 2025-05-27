
import pandas as pd
import re
import streamlit as st
import os

# Load primary data and reference image/submittal data
@st.cache_data
def load_data():
    base_path = os.path.dirname(__file__)
    df_main = pd.read_excel(os.path.join(base_path, "Updated File - 3-24.xlsx"), sheet_name="Export")
    df_ref = pd.read_excel(os.path.join(base_path, "Image.xlsx"), sheet_name="Sheet1")

    # Normalize for lookup
    df_main["Normalized Haydon Part"] = df_main["Haydon Part #"].apply(normalize)
    df_main["Normalized Vendor Part"] = df_main["Vendor Part #"].apply(normalize)
    df_ref["Normalized Name"] = df_ref["Name"].apply(normalize)

    return df_main, df_ref

# Normalization function
def normalize(part):
    if pd.isna(part):
        return ""
    return re.sub(r"[^A-Za-z0-9]", "", str(part)).lower()

# Core part extraction for Haydon (e.g., from H-132-HDG X 10 → H-132)
def extract_core_part(part_number):
    if pd.isna(part_number):
        return ""
    match = re.match(r"([A-Z]+-[0-9]+)", str(part_number), re.IGNORECASE)
    return match.group(1).upper() if match else part_number.strip().upper()

# Streamlit UI
st.set_page_config(layout="wide")
st.title("Haydon Cross-Reference with Product Images & Submittals")

query = st.text_input("Enter Haydon or Vendor part number:")

if query:
    df_main, df_ref = load_data()
    normalized_query = normalize(query)
    matches = df_main[
        df_main["Normalized Haydon Part"].str.contains(normalized_query, na=False) |
        df_main["Normalized Vendor Part"].str.contains(normalized_query, na=False)
    ]

    if not matches.empty:
        st.write(f"Found {len(matches)} matching entry(ies):")
        st.dataframe(matches.drop(columns=["Normalized Haydon Part", "Normalized Vendor Part"]))

        with st.sidebar:
            st.subheader("Product Details")
            first = matches.iloc[0]
            haydon_part = first["Haydon Part #"]
            core_part = extract_core_part(haydon_part)
            normalized_core = normalize(core_part)

            matched_ref = df_ref[df_ref["Normalized Name"] == normalized_core]
            if not matched_ref.empty:
                item = matched_ref.iloc[0]

                if pd.notna(item["Cover Image"]):
                    st.image(item["Cover Image"], caption=core_part, width=250)

                if pd.notna(item["Files"]):
                    st.markdown(f"📄 [View Submittal]({item['Files']})", unsafe_allow_html=True)
                else:
                    st.info("No submittal file available.")
            else:
                st.info("No product image/submittal found in reference list.")
    else:
        st.warning("No cross-reference found for that part number.")
