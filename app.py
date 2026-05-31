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

TARGET_URL = "
