import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

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
# RESTORE SUPABASE SESSION
# =========================================================
if (
    "access_token" in st.session_state
    and "refresh_token" in st.session_state
):
    try:
        supabase.auth.set_session(
            st.session_state["access_token"],
            st.session_state["refresh_token"]
        )
    except Exception:
        pass


# =========================================================
# LOGIN CHECK
# =========================================================
if "user" not in st.session_state or not st.session_state["user"]:
    st.warning("Please log in first.")
    st.stop()

user = st.session_state["user"]


# =========================================================
# USER SETTINGS
# =========================================================
try:
    metadata = user.user_metadata or {}
except Exception:
    metadata = {}


display_name = metadata.get(
    "display_name",
    ""
)

settings_currency = metadata.get(
    "currency",
    "₹ INR"
)

settings_categories = metadata.get(
    "custom_categories",
    []
)

settings_accounts = metadata.get(
    "custom_accounts",
    []
)


# =========================================================
# CURRENCY
# =========================================================
CURRENCY_SYMBOLS = {
    "₹ INR": "₹",
    "$ USD": "$",
    "€ EUR": "€",
    "£ GBP": "£",
    "¥ JPY": "¥",
    "₩ KRW": "₩",
    "AED": "AED ",
    "SGD": "SGD "
}

currency_symbol = CURRENCY_SYMBOLS.get(
    settings_currency,
    "₹"
)


def money(value):
    try:
        return f"{currency_symbol}{float(value):,.2f}"
    except Exception:
        return f"{currency_symbol}0.00"


# =========================================================
# HEADER
# =========================================================
if display_name.strip():

    st.title(
        f"💰 Welcome, {display_name.strip()}"
    )

else:

    st.title("💰 MoneyMate")

st.caption(
    "Personal Finance Dashboard"
)


# =========================================================
# LOAD TRANSACTIONS
# =========================================================
try:

    transaction_response = (
        supabase
        .table("transactions")
        .select("*")
        .eq("user_id", user.id)
        .order("date", desc=True)
        .execute()
    )

    transaction_data = (
        transaction_response.data or []
    )

    df = pd.DataFrame(
        transaction_data
    )

except Exception as e:

    st.error(
        f"Unable to load transactions: {e}"
    )

    st.stop()


# =========================================================
# PREPARE TRANSACTION DATA
# =========================================================
if df.empty:

    df = pd.DataFrame(
        columns=[
            "id",
            "date",
            "type",
            "amount",
            "category",
            "account",
            "note"
        ]
    )


if "amount" not in df.columns:

    df["amount"] = 0.0

else:

    df["amount"] = (
        df["amount"]
        .astype(str)
        .str.replace(
            "₹",
            "",
            regex=False
        )
        .str.replace(
            ",",
            "",
            regex=False
        )
        .str.strip()
    )

    df["amount"] = pd.to_numeric(
        df["amount"],
        errors="coerce"
    ).fillna(0.0)


if "type" not in df.columns:

    df["type"] = ""

else:

    df["type"] = (
        df["type"]
        .astype(str)
        .str.strip()
        .str.lower()
    )


if "category" not in df.columns:

    df["category"] = ""

else:

    df["category"] = (
        df["category"]
        .astype(str)
        .str.strip()
    )


if "account" not in df.columns:

    df["account"] = ""

else:

    df["account"] = (
        df["account"]
        .astype(str)
        .str.strip()
    )


if "date" not in df.columns:

    df["date"] = pd.NaT

else:

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )


# =========================================================
# ALL-TIME TOTALS
# =========================================================
total_income = float(
    df.loc[
        df["type"] == "income",
        "amount"
    ].sum()
)

total_expense = float(
    df.loc[
        df["type"] == "expense",
        "amount"
    ].sum()
)

total_balance = (
    total_income -
    total_expense
)


# =========================================================
# SELECT MONTH
# =========================================================
selected_month = st.date_input(
    "📅 Dashboard Month",
    value=date.today().replace(day=1),
    key="dashboard_month"
)

month_start = selected_month.replace(day=1)

if month_start.month == 12:
    next_month = month_start.replace(
        year=month_start.year + 1,
        month=1
    )
else:
    next_month = month_start.replace(
        month=month_start.month + 1
    )


# =========================================================
# MONTHLY TRANSACTIONS
# =========================================================
month_df = df[
    (df["date"] >= pd.Timestamp(month_start))
    &
    (df["date"] < pd.Timestamp(next_month))
].copy()


# =========================================================
# MONTHLY TOTALS
# =========================================================
monthly_income = float(
    month_df.loc[
        month_df["type"] == "income",
        "amount"
    ].sum()
)

monthly_expense = float(
    month_df.loc[
        month_df["type"] == "expense",
        "amount"
    ].sum()
)

monthly_balance = (
    monthly_income -
    monthly_expense
)

if monthly_income > 0:
    savings_percentage = (
        monthly_balance /
        monthly_income
    ) * 100
else:
    savings_percentage = 0


# =========================================================
# OVERALL FINANCIAL SUMMARY
# =========================================================
st.divider()

st.subheader("📊 Overall Financial Summary")

a1, a2, a3 = st.columns(3)

with a1:
    st.metric(
        "All-Time Income",
        money(total_income)
    )

with a2:
    st.metric(
        "All-Time Expense",
        money(total_expense)
    )

with a3:
    st.metric(
        "All-Time Balance",
        money(total_balance)
    )


# =========================================================
# FINANCIAL OVERVIEW
# =========================================================
st.divider()

st.subheader(
    f"📊 Financial Overview — "
    f"{month_start.strftime('%B %Y')}"
)


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "💰 Income",
        money(monthly_income)
    )


with col2:

    st.metric(
        "💸 Expense",
        money(monthly_expense)
    )


with col3:

    st.metric(
        "🏦 Balance",
        money(monthly_balance)
    )


with col4:

    st.metric(
        "📊 Savings",
        f"{savings_percentage:.1f}%"
    )

# =========================================================
# EXPENSE BY CATEGORY
# =========================================================
st.divider()

st.subheader(
    "🥧 Expense by Category"
)


expense_df = month_df[
    month_df["type"] == "expense"
].copy()


if expense_df.empty:

    st.info(
        "No expenses recorded for this month."
    )

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


    with chart_col:

        fig = px.pie(
            category_expense,
            names="category",
            values="amount",
            hole=0.45,
            title="Monthly Expense Distribution"
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


    with table_col:

        st.markdown(
            "### 📋 Category Wise"
        )

        category_display = (
            category_expense
            .rename(
                columns={
                    "category": "Category",
                    "amount": "Amount"
                }
            )
            .copy()
        )

        category_display["Amount"] = (
            category_display["Amount"]
            .apply(money)
        )

        st.dataframe(
            category_display,
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# INCOME VS EXPENSE
# =========================================================
st.divider()

st.subheader(
    "📈 Income vs Expense"
)


if not df.empty:

    monthly_chart_df = df[
        df["date"].notna()
    ].copy()

    if not monthly_chart_df.empty:

        monthly_chart_df["month"] = (
            monthly_chart_df["date"]
            .dt.to_period("M")
            .astype(str)
        )

        monthly_summary = (
            monthly_chart_df
            .groupby(
                [
                    "month",
                    "type"
                ],
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
            yaxis_title=f"Amount ({currency_symbol.strip()})",
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

    else:

        st.info(
            "No dated transactions available."
        )

else:

    st.info(
        "No transactions available yet."
    )


# =========================================================
# BUDGET UTILIZATION CHART
# =========================================================
if not budget_summary.empty:

    st.divider()

    st.subheader(
        "📊 Budget vs Actual by Category"
    )

    budget_chart_df = budget_summary[
        [
            "Category",
            "Budget",
            "Actual"
        ]
    ].copy()

    budget_chart_df = budget_chart_df.melt(
        id_vars=["Category"],
        value_vars=[
            "Budget",
            "Actual"
        ],
        var_name="Type",
        value_name="Amount"
    )

    fig_budget = px.bar(
        budget_chart_df,
        x="Category",
        y="Amount",
        color="Type",
        barmode="group",
        title="Budget vs Actual"
    )

    fig_budget.update_layout(
        xaxis_title="Category",
        yaxis_title=f"Amount ({currency_symbol.strip()})",
        margin=dict(
            t=50,
            b=20,
            l=20,
            r=20
        )
    )

    st.plotly_chart(
        fig_budget,
        use_container_width=True
    )


# =========================================================
# RECENT TRANSACTIONS
# =========================================================
st.divider()

st.subheader(
    "📋 Recent Transactions"
)


if df.empty:

    st.info(
        "No transactions available yet."
    )

else:

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
        .sort_values(
            "date",
            ascending=False
        )
        .head(10)
        .copy()
    )


    if "type" in recent_df.columns:

        recent_df["type"] = (
            recent_df["type"]
            .str.title()
        )


    if "date" in recent_df.columns:

        recent_df["date"] = (
            recent_df["date"]
            .dt.strftime("%d-%m-%Y")
        )


    if "amount" in recent_df.columns:

        recent_df["amount"] = (
            recent_df["amount"]
            .apply(money)
        )


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
# ACCOUNT SUMMARY
# =========================================================
st.divider()

st.subheader(
    "🏦 Account Summary"
)


account_df = month_df[
    month_df["account"].astype(str).str.strip() != ""
].copy()


if account_df.empty:

    st.info(
        "No account transactions for this month."
    )

else:

    account_summary = (
        account_df
        .groupby(
            [
                "account",
                "type"
            ],
            as_index=False
        )["amount"]
        .sum()
    )

    account_display = (
        account_summary
        .pivot(
            index="account",
            columns="type",
            values="amount"
        )
        .fillna(0)
        .reset_index()
    )

    if "income" not in account_display.columns:

        account_display["income"] = 0.0

    if "expense" not in account_display.columns:

        account_display["expense"] = 0.0


    account_display["Balance"] = (
        account_display["income"]
        -
        account_display["expense"]
    )


    account_display = (
        account_display
        .rename(
            columns={
                "account": "Account",
                "income": "Income",
                "expense": "Expense"
            }
        )
    )


    for column in [
        "Income",
        "Expense",
        "Balance"
    ]:

        account_display[column] = (
            account_display[column]
            .apply(money)
        )


    st.dataframe(
        account_display[
            [
                "Account",
                "Income",
                "Expense",
                "Balance"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# FOOTER
# =========================================================
st.divider()

st.caption(
    f"💰 MoneyMate • Personal Finance Dashboard • "
    f"Currency: {settings_currency}"
)

