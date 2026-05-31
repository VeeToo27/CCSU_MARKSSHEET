import os
import subprocess
import streamlit as st
from playwright.sync_api import sync_playwright

@st.cache_resource
def install_browser():
    try:
        subprocess.run(
            ["playwright", "install", "chromium"],
            check=True,
            capture_output=True,
            text=True
        )
    except Exception as e:
        st.warning(f"Browser install message: {e}")

install_browser()

st.title("Playwright Test")

url = st.text_input("URL", "https://example.com")

if st.button("Open"):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage"
                ]
            )

            page = browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=60000)

            st.success(f"Title: {page.title()}")

            screenshot = page.screenshot()
            st.image(screenshot)

            browser.close()

    except Exception as e:
        st.error(str(e))
