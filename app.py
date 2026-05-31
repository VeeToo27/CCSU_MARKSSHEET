import streamlit as st
import requests
from bs4 import BeautifulSoup

url = st.text_input("URL")

if st.button("Fetch Source"):
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    st.code(r.text, language="html")
