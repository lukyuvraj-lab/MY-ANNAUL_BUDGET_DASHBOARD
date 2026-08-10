import streamlit as st
import pandas as pd
import plotly.express as px

from utils.supabase_client import supabase


# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="MoneyMate Dashboard",
    page_icon="💰",
    layout="wide"
)


# =========================================================
# LOGIN CHECK
# =========================================================
if "user" not in st.session_state:
    st.warning("Please log in first.")
    st.stop()


# =========================================================
# HEADER
# =========================================================
st.title("💰 MoneyMate")
st.caption("Personal Finance Dashboard")


# =========================================================
# LOAD TRANSACTIONS
# =========================================================
try:
    response = (
        supabase
        .table("transactions")
        .select("*")
        .order("date", desc=True)
        .execute()
    )

    data = response.data

except Exception as e:
    st.error(f"Unable to load transactions: {e}")
    st.stop()


# =========================================================
# DATAFRAME
# =========================================================
df = pd.DataFrame(data)


# =========================================================
# NO DATA
# =========================================================
if df.empty:
    st.info("📋 No transactions available yet.")
    st.stop()


# =========================================================
# CLEAN DATA
# =========================================================
if "amount" in df.columns:
    df["amount"] = pd.to_numeric(
        df["amount"],
        errors="coerce"
    ).fillna(0)


if "type" in df.columns:
    df["type"] = (
        df["type"]
        .astype(str)
        .str.strip()
        .str.lower()
    )


# =========================================================
# CALCULATE TOTALS
# =========================================================
income = df.loc[
    df["type"] == "income",
    "amount"
].sum()

expense = df.loc[
    df["type"] == "expense",
    "amount"
].sum()

balance = income - expense


if income > 0:
    savings_percentage = (
        balance / income
    ) * 100
else:
    savings_percentage = 0


# =========================================================
# KPI CARDS
# =========================================================
st.subheader("📊 Financial Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "💰 Total Income",
        f"₹{income:,.2f}"
    )

with col2:
    st.metric(
        "💸 Total Expense",
        f"₹{expense:,.2f}"
    )

with col3:
    st.metric(
        "🏦 Balance",
        f"₹{balance:,.2f}"
    )

with col4:
    st.metric(
        "📊 Savings %",
        f"{savings_percentage:.1f}%"
    )


st.divider()


# =========================================================
# EXPENSE BY CATEGORY
# =========================================================
st.subheader("🥧 Expense by Category")

expense_df = df[
    df["type"] == "expense"
].copy()


if expense_df.empty:

    st.info("No expense transactions available.")

else:

    category_expense = (
        expense_df
        .groupby(
            "category",
            as_index=False
        )["amount"]
        .sum()
        .sort_values(
            "amount",
            ascending=False
        )
    )

    chart_col, table_col = st.columns(
        [1.4, 1]
    )

    # -----------------------------------------------------
    # PIE CHART
    # -----------------------------------------------------
    with chart_col:

        fig = px.pie(
            category_expense,
            names="category",
            values="amount",
            hole=0.45,
            title="Expense Distribution"
        )

        fig.update_layout(
            margin=dict(
                t=50,
                b=10,
                l=10,
                r=10
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # -----------------------------------------------------
    # CATEGORY TABLE
    # -----------------------------------------------------
    with table_col:

        st.markdown("### 📋 Category Wise")

        category_display = (
            category_expense
            .rename(
                columns={
                    "category": "Category",
                    "amount": "Amount"
                }
            )
        )

        category_display["Amount"] = (
            category_display["Amount"]
            .apply(lambda x: f"₹{x:,.2f}")
        )

        st.dataframe(
            category_display,
            use_container_width=True,
            hide_index=True
        )


st.divider()


# =========================================================
# INCOME VS EXPENSE
# =========================================================
st.subheader("📈 Income vs Expense")


if "date" in df.columns:

    monthly_df = df.copy()

    monthly_df["date"] = pd.to_datetime(
        monthly_df["date"],
        errors="coerce"
    )

    monthly_df = monthly_df.dropna(
        subset=["date"]
    )

    if not monthly_df.empty:

        monthly_df["month"] = (
            monthly_df["date"]
            .dt.to_period("M")
            .astype(str)
        )

        monthly_summary = (
            monthly_df
            .groupby(
                ["month", "type"],
                as_index=False
            )["amount"]
            .sum()
        )

        monthly_summary["type"] = (
            monthly_summary["type"]
            .str.title()
        )

        fig_monthly = px.bar(
            monthly_summary,
            x="month",
            y="amount",
            color="type",
            barmode="group",
            title="Monthly Income vs Expense"
        )

        fig_monthly.update_layout(
            xaxis_title="Month",
            yaxis_title="Amount (₹)",
            margin=dict(
                t=50,
                b=20,
                l=20,
                r=20
            )
        )

        st.plotly_chart(
            fig_monthly,
            use_container_width=True
        )


st.divider()


# =========================================================
# RECENT TRANSACTIONS
# =========================================================
st.subheader("📋 Recent Transactions")

recent_columns = [
    "date",
    "type",
    "category",
    "account",
    "amount",
    "note"
]

available_columns = [
    column
    for column in recent_columns
    if column in df.columns
]

recent_df = (
    df[
        available_columns
    ]
    .head(10)
    .copy()
)


# Format type
if "type" in recent_df.columns:

    recent_df["type"] = (
        recent_df["type"]
        .str.title()
    )


# Format amount
if "amount" in recent_df.columns:

    recent_df["amount"] = (
        recent_df["amount"]
        .apply(
            lambda x: f"₹{x:,.2f}"
        )
    )


# Rename columns
recent_df = recent_df.rename(
    columns={
        "date": "Date",
        "type": "Type",
        "category": "Category",
        "account": "Account",
        "amount": "Amount",
        "note": "Note"
    }
)


st.dataframe(
    recent_df,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# FOOTER
# =========================================================
st.divider()

st.caption(
    "💰 MoneyMate • Personal Finance Dashboard"
)
