
import zipfile
import os

# Corrected Streamlit app code
script_content = """
import pandas as pd
import re
import streamlit as st
import os
import requests
from bs4 import BeautifulSoup

# Load and clean data
def load_data():
    file_path = os.path.join(os.path.dirname(__file__), "Updated File - 3-24.xlsx")
    df = pd.read_excel(file_path, sheet_name="Export", engine="openpyxl")
    df["Normalized Haydon Part"] = df["Haydon Part #"].apply(normalize)
    df["Normalized Vendor Part"] = df["Vendor Part #"].apply(normalize)
    return df

# Normalization function
def normalize(part):
    if pd.isna(part):
        return ""
    return re.sub(r"[^A-Za-z0-9]", "", str(part)).lower()

# Search function
def search_parts(df, query):
    normalized_query = normalize(query)
    return df[
        df["Normalized Haydon Part"].str.contains(normalized_query, na=False) |
        df["Normalized Vendor Part"].str.contains(normalized_query, na=False)
    ]

# Fetch image from Google (unofficial basic fallback)
def fetch_image(query):
    headers = {"User-Agent": "Mozilla/5.0"}
    search_url = f"https://www.google.com/search?tbm=isch&q={query}"
    try:
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        img_tag = soup.find("img")
        if img_tag and img_tag.get("src") and img_tag["src"].startswith("http"):
            return img_tag["src"]
    except Exception as e:
        st.error(f"Image lookup failed: {e}")
    return None

# Streamlit app
st.title("Haydon Cross-Reference Search")

query = st.text_input("Enter part number (Haydon or Vendor):")

if query:
    df = load_data()
    results = search_parts(df, query)

    if not results.empty:
        st.write(f"Found {len(results)} matching entries:")
        st.dataframe(results.drop(columns=["Normalized Haydon Part", "Normalized Vendor Part"]))

        # Try image preview for first matching competitor part
        first_row = results.iloc[0]
        competitor_name = first_row["Vendor"]
        competitor_part = first_row["Vendor Part #"]
        image_query = f"{competitor_name} {competitor_part}" if pd.notna(competitor_name) and pd.notna(competitor_part) else None

        if image_query:
            st.subheader("Image Preview")
            image_url = fetch_image(image_query)
            if image_url:
                st.image(image_url, caption=image_query, use_container_width=True)
            else:
                st.info("No valid image found for the selected part.")
    else:
        st.warning("No matches found.")
"""

# Updated requirements
requirements_content = "streamlit\npandas\nopenpyxl\nrequests\nbeautifulsoup4\n"

# Set up paths
base_dir = "/mnt/data/haydon_app_updated"
os.makedirs(base_dir, exist_ok=True)

# Write files
script_path = os.path.join(base_dir, "haydon_part_search.py")
requirements_path = os.path.join(base_dir, "requirements.txt")
excel_src = "/mnt/data/Updated File - 3-24.xlsx"
excel_dest = os.path.join(base_dir, "Updated File - 3-24.xlsx")

with open(script_path, "w") as f:
    f.write(script_content)

with open(requirements_path, "w") as f:
    f.write(requirements_content)

# Copy Excel file
import shutil
shutil.copyfile(excel_src, excel_dest)

# Create the ZIP archive
zip_path = "/mnt/data/haydon_cross_ref_app_updated.zip"
with zipfile.ZipFile(zip_path, 'w') as zipf:
    zipf.write(script_path, arcname="haydon_part_search.py")
    zipf.write(requirements_path, arcname="requirements.txt")
    zipf.write(excel_dest, arcname="Updated File - 3-24.xlsx")

zip_path
