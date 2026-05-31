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

async def monitor_network_traffic(url):
    logs = []
    async with async_playwright() as p:
        # Launch cloud-optimized chromium instance
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Monitor and catch API/Fetch/XHR responses
        async def handle_response(response):
            # Target asynchronous api patterns or standard data requests
            if response.request.resource_type in ["fetch", "xhr"]:
                try:
                    text_payload = await response.text()
                except Exception:
                    text_payload = "[Binary/Unreadable Data Content]"
                
                logs.append({
                    "url": response.url,
                    "status": response.status,
                    "method": response.request.method,
                    "body": text_payload
                })

        # Attach network event listener
        page.on("response", handle_response)
        
        try:
            # Load portal and wait for full DOM generation
            await page.goto(url, wait_until="networkidle", timeout=30000)
        except Exception as e:
            st.error(f"Execution Error: {str(e)}")
        finally:
            await browser.close()
            
    return logs

if st.button("🚀 Analyze Site & Track Cloud XHR Logs"):
    with st.spinner("Initializing Cloud Browser Instance (Playwright)..."):
        # Streamlit requires running async loops using standard run wrappers
        captured_logs = asyncio.run(monitor_network_traffic(TARGET_URL))
        
    if not captured_logs:
        st.warning("No asynchronous background traffic detected during page initialization.")
    else:
        st.success(f"Intercepted {len(captured_logs)} background Fetch/XHR cloud hits!")
        for idx, item in enumerate(captured_logs):
            with st.expander(f"🔹 [{item['method']}] {item['url'][:90]}... (Status: {item['status']})"):
                st.write("**Full Target Endpoint:**", item['url'])
                st.write("**Captured Response Payload:**")
                st.code(item['body'], language="json")
