import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import BytesIO

st.set_page_config(page_title="CCSU Result Collector")

st.title("CCSU Result Collector")

uploaded_file = st.file_uploader(
    "Upload Excel with Roll Numbers",
    type=["xlsx"]
)

if uploaded_file:
    rolls_df = pd.read_excel(uploaded_file)

    st.write("Roll Numbers Found:", len(rolls_df))

    captcha_text = st.text_input("Enter CAPTCHA")

    if st.button("Fetch Results"):

        session = requests.Session()

        all_results = []

        for _, row in rolls_df.iterrows():

            roll_no = str(row["RollNo"])

            payload = {
                # REPLACE THESE WITH REAL FIELD NAMES
                "rollno": roll_no,
                "captcha": captcha_text
            }

            response = session.post(
                "https://result.ccsuniversityweb.in/",
                data=payload
            )

            soup = BeautifulSoup(response.text, "lxml")

            try:
                student_name = soup.select_one(
                    ".student-name"
                ).text.strip()

                result_status = soup.select_one(
                    ".result-status"
                ).text.strip()

                all_results.append({
                    "RollNo": roll_no,
                    "Name": student_name,
                    "Result": result_status
                })

            except Exception as e:

                all_results.append({
                    "RollNo": roll_no,
                    "Name": "",
                    "Result": f"ERROR: {e}"
                })

        final_df = pd.DataFrame(all_results)

        final_df.to_excel(
            "ccsu_results.xlsx",
            index=False
        )

        st.dataframe(final_df)

        with open("ccsu_results.xlsx", "rb") as f:
            st.download_button(
                "Download Excel",
                f,
                file_name="ccsu_results.xlsx"
            )
