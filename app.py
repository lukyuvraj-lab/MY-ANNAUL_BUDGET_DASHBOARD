import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Annual Budget Dashboard",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Annual Budget Dashboard")

uploaded_file = st.file_uploader(
    "Upload your Annual Budget Excel",
    type=["xlsx"]
)

if uploaded_file is None:
    st.info("Upload your Excel file to continue.")
    st.stop()

# Read the first sheet
df = pd.read_excel(uploaded_file, sheet_name=0)

st.subheader("Budget Data")
st.dataframe(df, use_container_width=True)

# Detect numeric columns
numeric_cols = df.select_dtypes(include="number").columns.tolist()

if len(numeric_cols) >= 2:

    budget_col = numeric_cols[0]
    actual_col = numeric_cols[1]

    total_budget = df[budget_col].sum()
    total_actual = df[actual_col].sum()
    balance = total_budget - total_actual

    c1, c2, c3 = st.columns(3)

    c1.metric("Total Budget", f"₹{total_budget:,.0f}")
    c2.metric("Total Spent", f"₹{total_actual:,.0f}")
    c3.metric("Remaining", f"₹{balance:,.0f}")

    if len(df.columns) >= 3:

        x_col = df.columns[0]

        fig = px.bar(
            df,
            x=x_col,
            y=[budget_col, actual_col],
            barmode="group",
            title="Budget vs Actual"
        )

        st.plotly_chart(fig, use_container_width=True)

    if len(df.columns) >= 2:

        cat_col = df.columns[0]

        pie = px.pie(
            df,
            names=cat_col,
            values=actual_col,
            title="Expense Distribution"
        )

        st.plotly_chart(pie, use_container_width=True)

else:
    st.warning("No numeric budget columns found.")
