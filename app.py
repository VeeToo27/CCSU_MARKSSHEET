import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# App configurations
st.set_page_config(
    page_title="CCSU Portal Viewer", 
    page_icon="🎓", 
    layout="wide"
)

st.title("🎓 CCSU Result Portal Gateway")
st.caption("Accessing: https://result.ccsuniversityweb.in/ safely via cloud container.")

TARGET_URL = "https://result.ccsuniversityweb.in/"

@st.cache_data(ttl=300) # Caches the webpage for 5 minutes to maintain quick performance
def load_university_portal(url):
    # Added real browser user-agent string to prevent cloud hosting bot-blocks
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.text
        return f"Portal Error: Server returned status code {response.status_code}"
    except Exception as e:
        return f"Proxy connection failure: {str(e)}"

# Execute server retrieval
html_raw = load_university_portal(TARGET_URL)

if "Error" in html_raw or "failure" in html_raw:
    st.error(html_raw)
    st.markdown(f"👉 [Click here to open the CCSU Result page directly]({TARGET_URL})")
else:
    # Compile raw elements and rewrite target assets to secure full paths
    soup = BeautifulSoup(html_raw, "html.parser")
    
    for asset in soup.find_all(["link", "script", "img", "form"]):
        if asset.has_attr("href"):
            asset["href"] = urljoin(TARGET_URL, asset["href"])
        if asset.has_attr("src"):
            asset["src"] = urljoin(TARGET_URL, asset["src"])
        if asset.has_attr("action"):
            asset["action"] = urljoin(TARGET_URL, asset["action"])

    # Output full structural interface 
    st.components.v1.html(str(soup), height=1000, scrolling=True)

