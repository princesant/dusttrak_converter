import streamlit as st
import pandas as pd
from datetime import timedelta
import tempfile
import os

st.title("DustTrak DRX 8533 CSV Converter")
st.write("Upload your raw DustTrak CSV and download cleaned data.")

def convert_dusttrak_file(uploaded_file):
    lines = uploaded_file.getvalue().decode("utf-8").splitlines()

    start_date = None
    start_time = None

    for line in lines:
        parts = line.strip().split(",")
        if parts[0] == "Test Start Date":
            start_date = parts[1].strip()
        if parts[0] == "Test Start Time":
            start_time = parts[1].strip()

    if not start_date or not start_time:
        st.error("Could not find Test Start Date or Time.")
        return None

    start_timestamp = pd.to_datetime(start_date + " " + start_time, dayfirst=True)

    header_index = None
    for i, line in enumerate(lines):
        if line.startswith("Elapsed Time"):
            header_index = i
            break

    if header_index is None:
        st.error("Could not find data header row.")
        return None

    df = pd.read_csv(uploaded_file, skiprows=header_index)
    df.columns = [c.strip() for c in df.columns]

    df["Timestamp"] = [
        start_timestamp + timedelta(seconds=int(s))
        for s in df["Elapsed Time [s]"]
    ]

    pm_columns = ["PM1 [mg/m3]", "PM2.5 [mg/m3]", "PM10 [mg/m3]"]

    for col in pm_columns:
        if col in df.columns:
            df[col] = df[col] * 1000

    final_df = df[[
        "Timestamp",
        "PM1 [mg/m3]",
        "PM2.5 [mg/m3]",
        "PM10 [mg/m3]"
    ]]

    return final_df


uploaded_file = st.file_uploader("Upload DustTrak CSV", type=["csv"])

if uploaded_file:
    cleaned_df = convert_dusttrak_file(uploaded_file)

    if cleaned_df is not None:
        st.success("Conversion successful!")

        st.dataframe(cleaned_df.head())

        csv = cleaned_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="Download Cleaned CSV",
            data=csv,
            file_name="cleaned_dusttrak.csv",
            mime="text/csv",
        )
