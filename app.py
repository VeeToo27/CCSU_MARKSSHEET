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

    xhr_requests = []

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

            def handle_response(response):
                try:
                    req = response.request

                    if req.resource_type in ["xhr", "fetch"]:
                        xhr_requests.append({
                            "method": req.method,
                            "url": req.url,
                            "status": response.status
                        })

                except Exception:
                    pass

            page.on("response", handle_response)

            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=90000
            )

            page.wait_for_timeout(10000)

            st.success(f"Title: {page.title()}")

            screenshot = page.screenshot(full_page=True)
            st.image(screenshot)

            browser.close()

        st.subheader("Captured Fetch/XHR Requests")

        if xhr_requests:

            unique_urls = set()

            for req in xhr_requests:

                if req["url"] in unique_urls:
                    continue

                unique_urls.add(req["url"])

                st.code(
                    f'{req["status"]} | {req["method"]} | {req["url"]}'
                )

        else:
            st.warning("No Fetch/XHR requests detected.")

    except Exception as e:
        st.error(str(e))
