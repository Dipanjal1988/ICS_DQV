import streamlit as st

import pandas as pd

import matplotlib.pyplot as plt

import seaborn as sns

import io

from transformers import pipeline



# --- Page Config ---

st.set_page_config(page_title="ICS - Data Profiling Tool", layout="wide")

logo_url = "https://github.com/Dipanjal1988/ICS_DQV/blob/main/Infinite_Computer_Solutions_Logo.jpg"



# --- QA Pipeline ---

qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")



# --- Header ---

col1, col2 = st.columns([9, 1])

with col1:

    st.title("ICS - Data Profiling Tool")

with col2:

    st.image(logo_url, width=80)



# --- Sidebar Upload ---

st.sidebar.header("📤 Upload Data")

file = st.sidebar.file_uploader("Upload CSV or Excel File", type=["csv", "xlsx"])

sample_size = st.sidebar.slider("Sample Size", 100, 10000, 1000, step=100)



if file:

    df = pd.read_csv(file) if file.name.endswith("csv") else pd.read_excel(file)

    df = df.head(sample_size)



    # Tabs

    tab1, tab2, tab3, tab4, tab5 = st.tabs([

        "📊 Module 1: Data Profiler",

        "✅ Module 2: Data Quality",

        "📈 Module 3: Visual Analysis",

        "🤖 Module 4: Ask ICS Assistant",

        "📥 Module 5: Export"

    ])



    # --- Module 1: Data Profiler ---

    with tab1:

        st.subheader("📊 Structural Profiling Summary")

        summary = pd.DataFrame({

            "Data Type": df.dtypes,

            "Missing (%)": df.isnull().mean().round(2) * 100,

            "Unique": df.nunique()

        })

        st.dataframe(summary)



    # --- Module 2: Data Quality ---

    with tab2:

        st.subheader("✅ Basic Data Quality Checks")

        dq_stats = pd.DataFrame({

            "Column": df.columns,

            "Null Count": df.isnull().sum(),

            "Null %": df.isnull().mean().round(2) * 100,

            "Unique Count": df.nunique()

        })

        st.dataframe(dq_stats)



        st.divider()



        # Full Row Duplicates

        st.subheader("🔁 Full Row Duplicate Check")

        full_duplicates = df[df.duplicated(keep=False)]

        if not full_duplicates.empty:

            st.warning(f"⚠️ Found {len(full_duplicates)} full duplicate rows")

            st.dataframe(full_duplicates)

        else:

            st.success("✅ No full row duplicates found.")



        st.divider()



        # Key-Based Duplicates

        st.subheader("🔑 Key-Based Duplicate Check")

        selected_keys = st.multiselect("Select column(s) to define duplicates:", df.columns.tolist())

        if selected_keys:

            key_duplicates = df[df.duplicated(subset=selected_keys, keep=False)]

            if not key_duplicates.empty:

                st.warning(f"⚠️ Found {len(key_duplicates)} duplicate rows based on selected keys")

                st.dataframe(key_duplicates)

            else:

                st.success("✅ No key-based duplicates found.")



    # --- Module 3: Visual Analysis ---

    with tab3:

        st.subheader("📈 Column Distribution")

        num_cols = df.select_dtypes(include=["float64", "int64"]).columns

        if not num_cols.empty:

            selected_col = st.selectbox("Select Numeric Column", num_cols)

            fig, ax = plt.subplots()

            sns.histplot(df[selected_col], kde=True, ax=ax)

            ax.set_title(f"Distribution of {selected_col}")

            st.pyplot(fig)

        else:

            st.warning("No numeric columns to display.")



    # --- Module 4: Ask ICS Assistant ---

    with tab4:

        st.subheader("🤖 Ask ICS Assistant")

        st.markdown("Ask questions like:")

        st.code("Which columns have over 50% nulls?")

        st.code("How many unique values in column X?")

        st.code("Is column Y numeric?")

        question = st.text_input("Ask a question about your data")

        if question:

            context = ""

            for col in df.columns:

                context += f"Column {col} has type {df[col].dtype}, {df[col].isnull().sum()} nulls, and {df[col].nunique()} unique values.\n"

            result = qa_pipeline(question=question, context=context)

            st.success(result['answer'])



    # --- Module 5: Export ---

    with tab5:

        st.subheader("📥 Export Full Profiling Summary")



        summary_df = summary.reset_index().rename(columns={'index': 'Column'})

        dq_stats_df = dq_stats



        # Histogram Summary

        hist_summary = pd.DataFrame()

        if not num_cols.empty:

            col = num_cols[0]

            hist_summary = pd.DataFrame({

                "Metric": ["Column", "Mean", "Std Dev", "Min", "Max"],

                "Value": [col, df[col].mean(), df[col].std(), df[col].min(), df[col].max()]

            })



        # CSV Export

        with io.StringIO() as csv_buffer:

            csv_buffer.write("=== Structural Profiling Summary ===\n")

            summary_df.to_csv(csv_buffer, index=False)

            csv_buffer.write("\n=== Data Quality Checks ===\n")

            dq_stats_df.to_csv(csv_buffer, index=False)

            if not hist_summary.empty:

                csv_buffer.write("\n=== Histogram Summary ===\n")

                hist_summary.to_csv(csv_buffer, index=False)



            st.download_button(

                label="Download Combined CSV",

                data=csv_buffer.getvalue(),

                file_name="ICS_Data_Profiler_All_Modules.csv",

                mime="text/csv"

            )



        # Excel Export

        excel_buffer = io.BytesIO()

        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:

            summary_df.to_excel(writer, sheet_name='Profiling Summary', index=False)

            dq_stats_df.to_excel(writer, sheet_name='Data Quality Checks', index=False)

            if not hist_summary.empty:

                hist_summary.to_excel(writer, sheet_name='Histogram Summary', index=False)



        st.download_button(

            label="Download Combined Excel",

            data=excel_buffer,

            file_name="ICS_Data_Profiler_All_Modules.xlsx",

            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        )



else:

    st.info("📥 Upload a CSV or Excel file to begin.")
