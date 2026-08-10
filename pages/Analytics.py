import streamlit as st
import pandas as pd
import plotly.express as px

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="MoneyMate - Analytics",
    page_icon="📊",
    layout="wide"
)

st.title("📊 MoneyMate - Analytics")
st.caption("Personal Finance Analytics Dashboard")


# ============================================================
# CATEGORY LIST
# ============================================================

income_categories = [
    "Salary",
    "Business",
    "Interest",
    "Balance Last Year",
    "Chit Fund",
    "Freelance",
    "Bouns",
    "Invesment",
    "Rental",
    "Refunds",
    "Commission",
    "Sales",
    "Tax Refunds",
    "Other Income"
]

expense_categories = [
    "Food & Dining",
    "Travel",
    "Transportation",
    "Shopping",
    "Housing",
    "Utilities",
    "Healthcare",
    "Education",
    "Emi/Loan",
    "Insurance",
    "Personal Care",
    "Family",
    "Bills",
    "Taxes",
    "Charity",
    "Bakery",
    "Beating",
    "Bike Maintenance",
    "Bills",
    "Business Invesment",
    "Chit Fund",
    "Entertainment",
    "Gifts",
    "Groceries/vegetable's",
    "Investment",
    "Home",
    "Employee Salaries",
    "Fuel",
    "Rent",
    "Subscriptions",
    "Recharge",
    "Mobile",
    "Taxes",
    "Interest",
    "Other Expense"
]

months = [
    "Jan", "Feb", "Mar", "Apr",
    "May", "Jun", "Jul", "Aug",
    "Sep", "Oct", "Nov", "Dec"
]


# ============================================================
# LOAD SUPABASE
# ============================================================

try:
    from utils.supabase_client import supabase

except Exception as e:
    st.error(
        "Unable to connect to Supabase. "
        f"Check utils/supabase_client.py: {e}"
    )
    st.stop()


# ============================================================
# LOAD TRANSACTIONS
# ============================================================

try:
    response = (
        supabase
        .table("transactions")
        .select("*")
        .order("date", desc=True)
        .execute()
    )

    data = response.data or []

except Exception as e:
    st.error(
        f"Unable to load transactions: {e}"
    )
    st.stop()


if not data:
    st.info("No transactions found.")
    st.stop()


df = pd.DataFrame(data)


# ============================================================
# VALIDATE DATA
# ============================================================

required_columns = [
    "date",
    "type",
    "amount",
    "category",
    "account"
]

missing_columns = [
    col
    for col in required_columns
    if col not in df.columns
]

if missing_columns:
    st.error(
        "Missing transaction columns: "
        + ", ".join(missing_columns)
    )
    st.stop()


# ============================================================
# CLEAN DATA
# ============================================================

df["date"] = pd.to_datetime(
    df["date"],
    errors="coerce"
)

df["amount"] = pd.to_numeric(
    df["amount"],
    errors="coerce"
).fillna(0)

df["type"] = (
    df["type"]
    .fillna("")
    .astype(str)
    .str.strip()
    .str.lower()
)

df["category"] = (
    df["category"]
    .fillna("")
    .astype(str)
    .str.strip()
)

df["account"] = (
    df["account"]
    .fillna("")
    .astype(str)
    .str.strip()
)

df = df.dropna(
    subset=["date"]
).copy()

if df.empty:
    st.info("No valid transactions found.")
    st.stop()

df["Year"] = df["date"].dt.year
df["Month Number"] = df["date"].dt.month
df["Month"] = df["date"].dt.strftime("%b")


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("🔎 Analytics Filters")

available_years = sorted(
    df["Year"].unique(),
    reverse=True
)

selected_year = st.sidebar.selectbox(
    "📅 Year",
    available_years
)

year_data = df[
    df["Year"] == selected_year
].copy()


available_months = sorted(
    year_data["Month Number"].unique()
)

selected_months = st.sidebar.multiselect(
    "📆 Months",
    options=list(range(1, 13)),
    default=list(range(1, 13)),
    format_func=lambda x: months[x - 1]
)

if selected_months:
    filtered_df = year_data[
        year_data["Month Number"].isin(
            selected_months
        )
    ].copy()
else:
    filtered_df = year_data.iloc[0:0].copy()


type_options = ["Income", "Expense"]

selected_types = st.sidebar.multiselect(
    "Transaction Type",
    options=type_options,
    default=type_options
)

filtered_df = filtered_df[
    filtered_df["type"].isin(
        [x.lower() for x in selected_types]
    )
].copy()


account_options = sorted(
    [
        x for x in
        df["account"].dropna().unique()
        if str(x).strip()
    ]
)

selected_accounts = st.sidebar.multiselect(
    "🏦 Account",
    options=account_options,
    default=account_options
)

if selected_accounts:
    filtered_df = filtered_df[
        filtered_df["account"].isin(
            selected_accounts
        )
    ].copy()


# ============================================================
# KPI CALCULATIONS
# ============================================================

income_df = filtered_df[
    filtered_df["type"] == "income"
]

expense_df = filtered_df[
    filtered_df["type"] == "expense"
]

total_income = income_df["amount"].sum()
total_expense = expense_df["amount"].sum()
balance = total_income - total_expense

spend_percent = (
    total_expense / total_income * 100
    if total_income > 0
    else 0
)


# ============================================================
# KPI CARDS
# ============================================================

st.subheader(
    f"📊 {selected_year} Analytics"
)

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "💰 Income",
    f"₹{total_income:,.2f}"
)

c2.metric(
    "💸 Expense",
    f"₹{total_expense:,.2f}"
)

c3.metric(
    "🏦 Balance",
    f"₹{balance:,.2f}"
)

c4.metric(
    "📉 Spend %",
    f"{spend_percent:.2f}%"
)


if filtered_df.empty:
    st.warning(
        "No transactions match the selected filters."
    )
    st.stop()


st.divider()


# ============================================================
# MONTHLY INCOME VS EXPENSE
# ============================================================

st.subheader("📈 Monthly Income vs Expense")

monthly = (
    filtered_df
    .groupby(
        ["Month Number", "Month", "type"],
        as_index=False
    )["amount"]
    .sum()
)

monthly["Type"] = (
    monthly["type"]
    .str.title()
)

monthly_chart = px.bar(
    monthly,
    x="Month",
    y="amount",
    color="Type",
    barmode="group",
    category_orders={
        "Month": months,
        "Type": ["Income", "Expense"]
    },
    labels={
        "amount": "Amount (₹)",
        "Month": "Month",
        "Type": "Type"
    },
    title=f"Monthly Income vs Expense - {selected_year}"
)

monthly_chart.update_layout(
    xaxis_title="Month",
    yaxis_title="Amount (₹)",
    legend_title="",
    hovermode="x unified"
)

st.plotly_chart(
    monthly_chart,
    use_container_width=True
)


# ============================================================
# EXPENSE BY CATEGORY
# ============================================================

st.subheader("💸 Expense by Category")

category_expense = (
    expense_df
    .groupby("category", as_index=False)["amount"]
    .sum()
    .sort_values(
        "amount",
        ascending=False
    )
)

if category_expense.empty:
    st.info("No expense data for the selected filters.")
else:

    left, right = st.columns(2)

    with left:

        category_bar = px.bar(
            category_expense.head(15),
            x="amount",
            y="category",
            orientation="h",
            labels={
                "amount": "Expense (₹)",
                "category": "Category"
            },
            title="Top 15 Expense Categories"
        )

        category_bar.update_layout(
            yaxis={
                "categoryorder": "total ascending"
            }
        )

        st.plotly_chart(
            category_bar,
            use_container_width=True
        )

    with right:

        category_pie = px.pie(
            category_expense,
            names="category",
            values="amount",
            title="Expense Distribution"
        )

        st.plotly_chart(
            category_pie,
            use_container_width=True
        )


# ============================================================
# INCOME BY CATEGORY
# ============================================================

st.subheader("💰 Income by Category")

category_income = (
    income_df
    .groupby("category", as_index=False)["amount"]
    .sum()
    .sort_values(
        "amount",
        ascending=False
    )
)

if category_income.empty:
    st.info("No income data for the selected filters.")
else:

    income_chart = px.bar(
        category_income,
        x="category",
        y="amount",
        labels={
            "amount": "Income (₹)",
            "category": "Category"
        },
        title="Income by Category"
    )

    income_chart.update_layout(
        xaxis_tickangle=-45
    )

    st.plotly_chart(
        income_chart,
        use_container_width=True
    )


# ============================================================
# ACCOUNT ANALYSIS
# ============================================================

st.subheader("🏦 Account Analysis")

account_summary = (
    filtered_df
    .groupby(
        ["account", "type"],
        as_index=False
    )["amount"]
    .sum()
)

account_summary["Type"] = (
    account_summary["type"]
    .str.title()
)

account_chart = px.bar(
    account_summary,
    x="account",
    y="amount",
    color="Type",
    barmode="group",
    labels={
        "amount": "Amount (₹)",
        "account": "Account",
        "Type": "Type"
    },
    title="Income and Expense by Account"
)

st.plotly_chart(
    account_chart,
    use_container_width=True
)


# ============================================================
# BALANCE TREND
# ============================================================

st.subheader("📊 Monthly Balance Trend")

balance_monthly = (
    filtered_df
    .groupby(
        ["Month Number", "Month", "type"],
        as_index=False
    )["amount"]
    .sum()
)

balance_pivot = (
    balance_monthly
    .pivot(
        index=["Month Number", "Month"],
        columns="type",
        values="amount"
    )
    .fillna(0)
    .reset_index()
)

if "income" not in balance_pivot.columns:
    balance_pivot["income"] = 0

if "expense" not in balance_pivot.columns:
    balance_pivot["expense"] = 0

balance_pivot["Balance"] = (
    balance_pivot["income"]
    -
    balance_pivot["expense"]
)

balance_pivot = balance_pivot.sort_values(
    "Month Number"
)

balance_chart = px.line(
    balance_pivot,
    x="Month",
    y="Balance",
    markers=True,
    labels={
        "Balance": "Balance (₹)",
        "Month": "Month"
    },
    title=f"Monthly Balance - {selected_year}"
)

st.plotly_chart(
    balance_chart,
    use_container_width=True
)


# ============================================================
# TOP EXPENSES
# ============================================================

st.subheader("🔝 Top Expenses")

top_expenses = (
    expense_df[
        [
            "date",
            "category",
            "account",
            "amount"
        ]
    ]
    .sort_values(
        "amount",
        ascending=False
    )
    .head(10)
    .copy()
)

top_expenses["date"] = (
    top_expenses["date"]
    .dt.strftime("%d-%m-%Y")
)

top_expenses = top_expenses.rename(
    columns={
        "date": "Date",
        "category": "Category",
        "account": "Account",
        "amount": "Amount"
    }
)

st.dataframe(
    top_expenses,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# CATEGORY SUMMARY TABLE
# ============================================================

st.subheader("📋 Category Summary")

category_summary = (
    filtered_df
    .groupby(
        ["category", "type"],
        as_index=False
    )["amount"]
    .sum()
)

category_summary["Type"] = (
    category_summary["type"]
    .str.title()
)

category_summary = category_summary[
    [
        "category",
        "Type",
        "amount"
    ]
].rename(
    columns={
        "category": "Category",
        "amount": "Amount"
    }
)

category_summary = category_summary.sort_values(
    "Amount",
    ascending=False
)

st.dataframe(
    category_summary,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# TRANSACTION COUNT
# ============================================================

st.subheader("🔢 Transaction Statistics")

s1, s2, s3 = st.columns(3)

s1.metric(
    "Total Transactions",
    f"{len(filtered_df):,}"
)

s2.metric(
    "Income Transactions",
    f"{len(income_df):,}"
)

s3.metric(
    "Expense Transactions",
    f"{len(expense_df):,}"
)


# ============================================================
# RAW TRANSACTIONS
# ============================================================

with st.expander("📄 View Transactions"):

    display_df = filtered_df.copy()

    display_df["date"] = (
        display_df["date"]
        .dt.strftime("%d-%m-%Y")
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

