import streamlit as st
import subprocess
from playwright.sync_api import sync_playwright

st.set_page_config(page_title="XHR Monitor", layout="wide")

@st.cache_resource
def install_browser():
    try:
        subprocess.run(
            ["playwright", "install", "chromium"],
            capture_output=True,
            text=True,
            check=False
        )
    except Exception:
        pass

install_browser()

st.title("Fetch / XHR Request Monitor")

url = st.text_input(
    "Enter URL",
    "https://www.youtube.com"
)

if st.button("Scan"):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    # Use session state to guarantee data persistence during the run
    st.session_state["xhr_requests"] = {}

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu"
                ]
            )
            
            page = browser.new_page()

            # Real-time deduplication using URL as a dictionary key
            def handle_response(response):
                try:
                    req = response.request
                    if req.resource_type in ["xhr", "fetch"]:
                        st.session_state["xhr_requests"][req.url] = {
                            "method": req.method,
                            "status": response.status
                        }
                except Exception:
                    pass

            page.on("response", handle_response)

            # Changed to networkidle to ensure background fetch requests complete
            page.goto(
                url,
                wait_until="networkidle",
                timeout=90000
            )

            page.wait_for_timeout(5000)

            st.success(f"Title: {page.title()}")
            
            screenshot = page.screenshot(full_page=False)
            st.image(screenshot)
            
            browser.close()

        st.subheader("Captured Fetch/XHR Requests")

        if st.session_state["xhr_requests"]:
            for req_url, data in st.session_state["xhr_requests"].items():
                st.code(
                    f'{data["status"]} | {data["method"]} | {req_url}'
                )
        else:
            st.warning("No Fetch/XHR requests detected.")

    except Exception as e:
        st.error(str(e))
