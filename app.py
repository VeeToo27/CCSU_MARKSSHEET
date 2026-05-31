import streamlit as st
import pandas as pd
from playwright.sync_api import sync_playwright

st.title("Marksheet Monitor")

if st.button("Start Browser"):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        page = browser.new_page()

        def handle_navigation(frame):
            url = frame.url

            if "marksheet" in url.lower():
                st.write("Marksheet detected")

                # extract data here
                data = {
                    "Roll": "123",
                    "Name": "Student",
                    "Maths": 85,
                    "Physics": 88
                }

                df = pd.DataFrame([data])

                try:
                    old = pd.read_excel("marks.xlsx")
                    df = pd.concat([old, df])
                except:
                    pass

                df.to_excel("marks.xlsx", index=False)

        page.on("framenavigated", handle_navigation)

        page.goto("https://example.com")
