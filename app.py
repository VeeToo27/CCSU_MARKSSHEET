import streamlit as st

# Set up the app layout and title
st.set_page_config(page_title="Streamlit Web Viewer", layout="wide")
st.title("🌐 Streamlit Web View Simulator")
st.caption("Note: Many major websites block iframe embedding for security reasons.")

# Add a text input bar for the URL
url_input = st.text_input(
    "Enter Website URL (include http:// or https://):", 
    value="https://wikipedia.org"
)

# Render the website using an iframe component
if url_input:
    st.markdown(f"### Viewing: {url_input}")
    
    # st.components.v1.html allows us to inject raw HTML code
    st.components.v1.html(
        f"""
        <iframe 
            src="{url_input}" 
            width="100%" 
            height="800px" 
            style="border:none; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);"
            sandbox="allow-scripts allow-same-origin allow-forms"
        >
        </iframe>
        """,
        height=820,
        scrolling=True
    )
