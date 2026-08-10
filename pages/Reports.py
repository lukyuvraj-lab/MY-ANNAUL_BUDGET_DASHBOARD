import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

from utils.supabase_client import supabase


# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="MoneyMate Reports",
    page_icon="📊",
    layout="wide"
)


# =========================================================
# RESTORE SUPABASE SESSION
# =========================================================
if (
    "access_token" in st.session_state
    and "refresh_token" in st.session_state
):
    supabase.auth.set_session(
        st.session_state["access_token"],
        st.session_state["refresh_token"]
    )


# =========================================================
# LOGIN CHECK
# =========================================================
if "user" not in st.session_state:
    st.warning("Please log in first.")
    st.stop()

user = st.session_state["user"]


# =========================================================
# TITLE
# =========================================================
st.title("📊 Reports")
st.caption("Monthly and yearly financial reports")


# =========================================================
# LOAD TRANSACTIONS
# =========================================================
try:

    response = (
        supabase
        .table("transactions")
        .select("*")
        .eq("user_id", user.id)
        .order("date", desc=False)
        .execute()
    )

    df = pd.DataFrame(response.data)

except Exception as e:

    st.error(f"Unable to load transactions: {e}")
    st.stop()


# =========================================================
# NO DATA
# =========================================================
if df.empty:

    st.info("📋 No transactions available yet.")
    st.stop()


# =========================================================
# PREPARE DATA
# =========================================================
df["date"] = pd.to_datetime(
    df["date"],
    errors="coerce"
)

df["amount"] = pd.to_numeric(
    df["amount"],
    errors="coerce"
).fillna(0)

df = df.dropna(
    subset=["date"]
)

df["year"] = df["date"].dt.year
df["month_number"] = df["date"].dt.month
df["month"] = df["date"].dt.strftime("%B")


# =========================================================
# YEAR SELECTOR
# =========================================================
available_years = sorted(
    df["year"].unique(),
    reverse=True
)

selected_year = st.selectbox(
    "📅 Select Year",
    available_years
)


# =========================================================
# SELECTED YEAR DATA
# =========================================================
year_df = df[
    df["year"] == selected_year
].copy()


# =========================================================
# YEARLY TOTALS
# =========================================================
income = year_df[
    year_df["type"] == "Income"
]["amount"].sum()

expense = year_df[
    year_df["type"] == "Expense"
]["amount"].sum()

balance = income - expense

if income > 0:
    savings = (
        balance / income
    ) * 100
else:
    savings = 0


# =========================================================
# KPI CARDS
# =========================================================
st.subheader(
    f"📊 {selected_year} Summary"
)

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "💰 Total Income",
    f"₹{income:,.2f}"
)

c2.metric(
    "💸 Total Expense",
    f"₹{expense:,.2f}"
)

c3.metric(
    "🏦 Balance",
    f"₹{balance:,.2f}"
)

c4.metric(
    "📊 Savings %",
    f"{savings:.1f}%"
)


# =========================================================
# MONTH-WISE REPORT
# =========================================================
st.divider()

st.subheader(
    "📋 Month-wise Report"
)


month_names = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
]


monthly_rows = []

for month_number, month_name in enumerate(
    month_names,
    start=1
):

    month_data = year_df[
        year_df["month_number"] == month_number
    ]

    month_income = month_data[
        month_data["type"] == "Income"
    ]["amount"].sum()

    month_expense = month_data[
        month_data["type"] == "Expense"
    ]["amount"].sum()

    month_balance = (
        month_income - month_expense
    )

    if month_income > 0:
        month_savings = (
            month_balance / month_income
        ) * 100
    else:
        month_savings = 0

    monthly_rows.append({
        "Month": month_name,
        "Income": month_income,
        "Expense": month_expense,
        "Balance": month_balance,
        "Savings %": month_savings
    })


monthly_df = pd.DataFrame(
    monthly_rows
)


# =========================================================
# DISPLAY MONTHLY TABLE
# =========================================================
display_monthly = monthly_df.copy()

display_monthly["Income"] = (
    display_monthly["Income"]
    .map(lambda x: f"₹{x:,.2f}")
)

display_monthly["Expense"] = (
    display_monthly["Expense"]
    .map(lambda x: f"₹{x:,.2f}")
)

display_monthly["Balance"] = (
    display_monthly["Balance"]
    .map(lambda x: f"₹{x:,.2f}")
)

display_monthly["Savings %"] = (
    display_monthly["Savings %"]
    .map(lambda x: f"{x:.1f}%")
)


st.dataframe(
    display_monthly,
    use_container_width=True,
   
