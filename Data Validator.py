import streamlit as st

import pandas as pd

import numpy as np

import os

import io

import matplotlib.pyplot as plt



# Set Streamlit page config

st.set_page_config(page_title="ICS - Data Validation Tool", layout="wide")



# Header with Tool Name and Logo

col1, col2 = st.columns([4, 1])

with col1:

    st.markdown("<h1 style='margin-bottom: 5px;'>ICS - Data Validation Tool</h1>", unsafe_allow_html=True)

with col2:

    logo_path = r"C:\Users\dipan\OneDrive\Documents\DVQ\Infinite_Computer_Solutions_Logo.jpg"

    st.image(logo_path, width=300)



# File Delivery Validation Section

st.subheader("1. File Delivery Validation")

col_left, col_right = st.columns(2)

with col_left:

    source_file = st.file_uploader("Upload Source Extract (CSV/XLSX)", type=["csv", "xlsx"])

with col_right:

    target_folder = st.text_input("Enter Target Folder Path to Validate Against:")



validation_summary = []



if source_file and target_folder:

    filename = source_file.name

    target_file_path = os.path.join(target_folder, filename)



    if os.path.exists(target_file_path):

        st.success(f"✅ Target file '{filename}' exists in: {target_folder}")

        validation_summary.append({

            "Module": "File Delivery",

            "Status": "Success",

            "Details": f"'{filename}' exists in target folder."

        })



        # Read files

        df_source = pd.read_csv(source_file) if filename.endswith("csv") else pd.read_excel(source_file)

        df_target = pd.read_csv(target_file_path) if filename.endswith("csv") else pd.read_excel(target_file_path)



        # Reset index to ensure alignment

        df_source.reset_index(drop=True, inplace=True)

        df_target.reset_index(drop=True, inplace=True)



        # Schema Match

        st.subheader("2. Schema Match Validation")

        source_cols = list(df_source.columns)

        target_cols = list(df_target.columns)

        st.write("Source Columns:", source_cols)

        st.write("Target Columns:", target_cols)



        schema_match = source_cols == target_cols

        if schema_match:

            st.success("✅ Columns match.")

            validation_summary.append({"Module": "Schema Match", "Status": "Success", "Details": "Columns match."})

        else:

            st.error("❌ Column names/order mismatch.")

            validation_summary.append({"Module": "Schema Match", "Status": "Fail", "Details": "Mismatch in column names/order."})

            st.warning(f"Missing in target: {[col for col in source_cols if col not in target_cols]}")

            st.warning(f"Extra in target: {[col for col in target_cols if col not in source_cols]}")



        # Row Count Validation

        st.subheader("3. Row Count Validation")

        source_len, target_len = len(df_source), len(df_target)

        st.write(f"Source Rows: {source_len}")

        st.write(f"Target Rows: {target_len}")



        row_match = source_len == target_len

        if row_match:

            st.success("✅ Row counts match.")

            validation_summary.append({"Module": "Row Count", "Status": "Success", "Details": "Row counts match."})

        else:

            st.error("❌ Row counts do NOT match.")

            validation_summary.append({

                "Module": "Row Count", "Status": "Fail",

                "Details": f"Source: {source_len}, Target: {target_len}"

            })



        # Data Matching (if schema matches)

        st.subheader("4. Data Matching")

        if schema_match:

            min_len = min(len(df_source), len(df_target))

            mismatches = (df_source.head(min_len) != df_target.head(min_len)).any(axis=1)

            mismatch_count = mismatches.sum()

            match_percent = round(((min_len - mismatch_count) / min_len) * 100, 2)

            mismatch_percent = round((mismatch_count / min_len) * 100, 2)



            st.write(f"✅ Match %: {match_percent}%")

            st.write(f"❌ Mismatch %: {mismatch_percent}%")



            validation_summary.append({

                "Module": "Data Match",

                "Status": "Success" if mismatch_count == 0 else "Partial",

                "Details": f"{match_percent}% match, {mismatch_count} mismatches"

            })



            # Pie chart

            fig, ax = plt.subplots()

            ax.pie([match_percent, mismatch_percent], labels=["Match", "Mismatch"], colors=["green", "red"], autopct='%1.1f%%')

            ax.set_title("Data Match Overview")

            st.pyplot(fig)



            # Show sample mismatches

            if mismatch_count > 0:

                st.subheader("Sample Mismatched Rows")

                for idx in mismatches[mismatches].index[:5]:

                    st.write(f"Row {idx}")

                    st.write("Source:", df_source.iloc[idx].to_dict())

                    st.write("Target:", df_target.iloc[idx].to_dict())

        else:

            st.warning("⚠️ Skipping data matching due to schema mismatch.")

            validation_summary.append({

                "Module": "Data Match",

                "Status": "Skipped",

                "Details": "Schema mismatch."

            })



        # Export Results

        st.subheader("📤 Export Validation Summary")

        result_df = pd.DataFrame(validation_summary)

        output = io.BytesIO()

        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:

            result_df.to_excel(writer, sheet_name="Validation Summary", index=False)

            df_source.to_excel(writer, sheet_name="Source Data", index=False)

            df_target.to_excel(writer, sheet_name="Target Data", index=False)

        st.download_button("Download Excel Report", output.getvalue(),

                           file_name="validation_report.xlsx",

                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")



    else:

        st.error(f"❌ File '{filename}' not found in target folder.")

        validation_summary.append({"Module": "File Delivery", "Status": "Fail",

                                   "Details": f"File not found in target path: {target_folder}"})

elif source_file and not target_folder:

    st.warning("⚠️ Please provide the target folder path to validate against.")

else:

    st.info("Upload a source file and enter target folder path to begin.")

