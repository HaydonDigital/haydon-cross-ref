
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

# Normalize part numbers by removing non-alphanumeric characters
def normalize(part):
    if pd.isna(part):
        return ""
    return re.sub(r"[^A-Za-z0-9]", "", str(part)).lower()

# Search across Haydon and Vendor parts
def search_parts(df, query):
    normalized_query = normalize(query)
    return df[
        df["Normalized Haydon Part"].str.contains(normalized_query, na=False) |
        df["Normalized Vendor Part"].str.contains(normalized_query, na=False)
    ]

# Extract core Haydon part for image URL
def extract_core_haydon_part(part_number):
    if pd.isna(part_number):
        return None
    match = re.match(r"([A-Z]+-[0-9]+)", str(part_number), re.IGNORECASE)
    return match.group(1).lower() if match else None

# Fetch product image from HaydonCorp product page
def fetch_haydon_image(haydon_part):
    part_code = extract_core_haydon_part(haydon_part)
    if not part_code:
        return None
    url = f"https://haydoncorp.com/catalog/product/{part_code}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
        soup = BeautifulSoup(response.text, "html.parser")
        image_tag = soup.find("img", {"class": "product-gallery__img"})
        if image_tag and image_tag.get("src"):
            return image_tag["src"]
    except:
        return None
    return None

# Fetch top 3 images from Google search
def fetch_google_images(query, max_images=3):
    headers = {"User-Agent": "Mozilla/5.0"}
    search_url = f"https://www.google.com/search?tbm=isch&q={query}"
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        img_tags = soup.find_all("img", limit=max_images + 1)
        img_urls = []
        for img in img_tags:
            src = img.get("src")
            if src and src.startswith("http"):
                img_urls.append(src)
        return img_urls[:max_images]
    except:
        return []

# Streamlit UI
st.title("Haydon Cross-Reference Search")

query = st.text_input("Enter part number (Haydon or Vendor):")

if query:
    df = load_data()
    results = search_parts(df, query)

    if not results.empty:
        st.write(f"Found {len(results)} matching entries:")
        st.dataframe(results.drop(columns=["Normalized Haydon Part", "Normalized Vendor Part"]))

        first_row = results.iloc[0]
        haydon_part = first_row["Haydon Part #"]

        st.subheader("Product Image (Haydon)")
        haydon_img_url = fetch_haydon_image(haydon_part)
        if haydon_img_url:
            st.image(haydon_img_url, caption=haydon_part, use_container_width=True)
        else:
            st.info("No image found for this Haydon part.")
    else:
        st.warning("No exact matches found in Haydon cross-reference.")
        brand = st.text_input("Enter the brand name for Google search (e.g. 'Unistrut'):")

        if brand:
            search_term = f"{brand} {query}"
            st.subheader(f"Top Google Image Results for: {search_term}")
            image_urls = fetch_google_images(search_term)
            if image_urls:
                for url in image_urls:
                    st.markdown(f'<a href="{url}" target="_blank"><img src="{url}" width="250" height="250" style="margin-right:10px;"/></a>', unsafe_allow_html=True)
            else:
                st.info("No images found on Google.")
