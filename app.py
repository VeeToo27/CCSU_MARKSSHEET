import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

st.set_page_config(page_title="Live Network Recorder", page_icon="📡", layout="wide")
st.title("📡 Live Web Interceptor & Recorder")
st.caption("Interact manually with the portal inside the frame below. Any background Fetch/XHR triggers will capture live on the right sidebar.")

TARGET_URL = "https://ccsuniversityweb.in"

# 1. Setup Persistent Session State variables to record captured data
if "captured_network_logs" not in st.session_state:
    st.session_state.captured_network_logs = []

# Sidebar panel layout configuration to review the captured activities
with st.sidebar:
    st.header("📊 Recorded Fetch/XHR Traffic")
    if st.button("🗑️ Clear Network Logs"):
        st.session_state.captured_network_logs = []
        st.rerun()
        
    if not st.session_state.captured_network_logs:
        st.info("No network actions captured yet. Input values or submit a form in the main view window to start recording.")
    else:
        for idx, item in enumerate(reversed(st.session_state.captured_network_logs)):
            with st.expander(f"🔹 [{item['type'].upper()}] {item['url'][:40]}...", expanded=(idx==0)):
                st.caption(f"**URL:** {item['url']}")
                st.caption(f"**Method:** {item.get('method', 'POST/GET')}")
                if item.get('payload'):
                    st.write("**Sent Request Data:**")
                    st.code(item['payload'])
                st.write("**Intercepted Server Response:**")
                st.code(item['response'], language="json")

# 2. Check for inbound intercepted XHR data packets transmitted via JavaScript bridge
# Streamlit components pass parameter values back from standard URL queries
query_params = st.query_params
if "network_data" in query_params:
    try:
        raw_payload = json.loads(query_params["network_data"])
        # Append incoming telemetry payloads into state tracking 
        if raw_payload not in st.session_state.captured_network_logs:
            st.session_state.captured_network_logs.append(raw_payload)
            st.rerun()
    except Exception as e:
        pass

# 3. Request proxy structure to acquire university layout 
@st.cache_data(ttl=60)
def get_proxied_dom_tree(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        return res.text if res.status_code == 200 else None
    except:
        return None

html_source = get_proxied_dom_tree(TARGET_URL)

if not html_source:
    st.error("Unable to link to university network servers. Please confirm the website endpoint is fully active.")
else:
    soup = BeautifulSoup(html_source, "html.parser")
    
    # 4. Standard path normalization for assets, formatting paths
    for asset in soup.find_all(["link", "script", "img", "form"]):
        if asset.has_attr("href"):
            asset["href"] = urljoin(TARGET_URL, asset["href"])
        if asset.has_attr("src"):
            asset["src"] = urljoin(TARGET_URL, asset["src"])
        if asset.has_attr("action"):
            asset["action"] = urljoin(TARGET_URL, asset["action"])

    # 5. Inject the JavaScript Monkeypatch Engine into the webpage header
    # This captures the native XHR/Fetch events and routes data securely to Streamlit
    interception_script = """
    <script>
    (function() {
        console.log("Network Interceptor Attached Successfully.");

        function sendTelemetryToStreamlit(type, url, method, payload, responseText) {
            const dataPackage = {
                type: type,
                url: url,
                method: method || 'UNKNOWN',
                payload: payload || '',
                response: responseText
            };
            // Send the network data across domains to the parent window
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: JSON.stringify(dataPackage)
            }, '*');
        }

        # Intercept Standard XMLHttpRequest (XHR) pipelines
        const oldXHR = window.XMLHttpRequest;
        function newXHR() {
            const realXHR = new oldXHR();
            let requestDetails = {};

            const oldOpen = realXHR.open;
            realXHR.open = function(method, url) {
                requestDetails.method = method;
                requestDetails.url = url;
                return oldOpen.apply(realXHR, arguments);
            };

            const oldSend = realXHR.send;
            realXHR.send = function(data) {
                requestDetails.payload = data;
                return oldSend.apply(realXHR, arguments);
            };

            realXHR.addEventListener('load', function() {
                sendTelemetryToStreamlit('xhr', requestDetails.url, requestDetails.method, requestDetails.payload, realXHR.responseText);
            });
            return realXHR;
        }
        window.XMLHttpRequest = newXHR;

        # Intercept standard modern Browser Fetch requests
        const oldFetch = window.fetch;
        window.fetch = async function(...args) {
            const url = args[0];
            const options = args[1] || {};
            const method = options.method || 'GET';
            const payload = options.body || '';

            const response = await oldFetch.apply(window, args);
            const clone = response.clone();
            
            clone.text().then(text => {
                sendTelemetryToStreamlit('fetch', url, method, payload, text);
            });

            return response;
        };
    })();
    </script>
    """
    
    # Place script container directly inside the top of the body parsing array
    if soup.body:
        soup.body.insert(0, BeautifulSoup(interception_script, "html.parser"))
    
    # 6. Render the Interactive Application Component Proxy
    # We create an inline custom component script frame that processes the postMessage callbacks
    st.components.v1.html(
        f"""
        <div id="wrapper">{str(soup)}</div>
        <script>
        // Catch messages emitted from inside our injected monkeypatch framework
        window.addEventListener('message', function(event) {{
            if (event.data && event.data.type === 'streamlit:setComponentValue') {{
                const encodedData = encodeURIComponent(event.data.value);
                // Push the data string directly back to Streamlit parameters
                window.parent.location.search = '?network_data=' + encodedData;
            }}
        }});
        </script>
        """,
        height=900,
        scrolling=True
    )
