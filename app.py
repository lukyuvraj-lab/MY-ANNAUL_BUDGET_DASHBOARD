import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Annual Budget Dashboard", layout="wide")

st.title("📊 Annual Budget Dashboard")

uploaded_file = st.file_uploader("Upload Annual Budget Excel", type=["xlsx"])

if uploaded_file is None:
    st.stop()

# Read sheets
month_df = pd.read_excel(uploaded_file, sheet_name="Budget by month")
year_df = pd.read_excel(uploaded_file, sheet_name=" Budget by year")

# ---------- CHANGE THESE COLUMN NAMES TO MATCH YOUR FILE ----------
income_col = "Income"
expense_col = "Expenses"
month_col = "Month"
category_col = "Category"
year_col = "Year"
# ---------------------------------------------------------------

# KPI
total_income = month_df[income_col].sum()
total_expense = month_df[expense_col].sum()
saving = total_income - total_expense
spend_pct = total_expense / total_income * 100
saving_pct = saving / total_income * 100

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Income", f"₹{total_income:,.0f}")
c2.metric("Expenses", f"₹{total_expense:,.0f}")
c3.metric("Savings", f"₹{saving:,.0f}")
c4.metric("Spend %", f"{spend_pct:.1f}%")
c5.metric("Savings %", f"{saving_pct:.1f}%")

st.divider()

# Month Filter
month = st.selectbox(
    "Select Month",
    ["All"] + list(month_df[month_col].dropna().unique())
)

if month != "All":
    filtered = month_df[month_df[month_col] == month]
else:
    filtered = month_df

col1, col2 = st.columns(2)

with col1:

    chart = px.bar(
        filtered,
        x=month_col,
        y=[income_col, expense_col],
        barmode="group",
        title="Income vs Expenses"
    )

    st.plotly_chart(chart, use_container_width=True)

with col2:

    donut = px.pie(
        filtered,
        names=category_col,
        values=expense_col,
        hole=0.55,
        title="Category Spend"
    )

    st.plotly_chart(donut, use_container_width=True)

st.subheader("Monthly Income")

st.dataframe(filtered)

# Year Summary
year_df["Savings"] = year_df[income_col] - year_df[expense_col]

fig = px.bar(
    year_df,
    x=year_col,
    y=[income_col, expense_col, "Savings"],
    barmode="group",
    title="Year Income vs Expenses vs Savings"
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Budget by Year")

st.dataframe(year_df)
