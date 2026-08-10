import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# ============================================================
# REPORTS PAGE
# ============================================================

st.set_page_config(
    page_title="MoneyMate - Reports",
    page_icon="📊",
    layout="wide"
)

st.title("📊 MoneyMate - Yearly Report")


# ============================================================
# LOAD TRANSACTIONS
# ============================================================

try:
    from utils.supabase_client import supabase

    response = (
        supabase
        .table("transactions")
        .select("*")
        .execute()
    )

    data = response.data

except Exception as e:
    st.error(f"Unable to load transactions: {e}")
    data = []


if not data:
    st.info("No transactions found.")
    st.stop()


df = pd.DataFrame(data)


# ============================================================
# PREPARE DATA
# ============================================================

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


# ============================================================
# YEAR SELECTOR
# ============================================================

available_years = sorted(
    df["date"].dt.year.unique(),
    reverse=True
)

selected_year = st.selectbox(
    "📅 Select Year",
    available_years
)

year_df = df[
    df["date"].dt.year == selected_year
].copy()


if year_df.empty:
    st.warning(
        "No transactions found for the selected year."
    )
    st.stop()


# ============================================================
# MONTHS
# ============================================================

months = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec"
]

year_df["Month"] = (
    year_df["date"].dt.month
)


# ============================================================
# 📊 YEARLY KPI SUMMARY
# ============================================================

income_mask = (
    year_df["type"]
    .astype(str)
    .str.lower()
    == "income"
)

expense_mask = (
    year_df["type"]
    .astype(str)
    .str.lower()
    == "expense"
)


total_income = year_df.loc[
    income_mask,
    "amount"
].sum()


total_expense = year_df.loc[
    expense_mask,
    "amount"
].sum()


total_savings = (
    total_income -
    total_expense
)


if total_income > 0:

    total_spend_percent = (
        total_expense /
        total_income
    ) * 100

else:

    total_spend_percent = 0


# ============================================================
# 💰 YEARLY SUMMARY CARDS
# ============================================================

st.subheader(
    f"📅 {selected_year} Overview"
)


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        label="💰 Total Income",
        value=f"₹{total_income:,.2f}"
    )


with col2:

    st.metric(
        label="💸 Total Expense",
        value=f"₹{total_expense:,.2f}"
    )


with col3:

    st.metric(
        label="🏦 Total Savings",
        value=f"₹{total_savings:,.2f}"
    )


with col4:

    st.metric(
        label="📊 Total Spend %",
        value=f"{total_spend_percent:.2f}%"
    )


st.divider()


# ============================================================
# 💰 INCOME
# ============================================================

st.subheader("💰 Income")


income_df = year_df[
    income_mask
].copy()


if income_df.empty:

    income_table = pd.DataFrame(
        columns=[
            "Category"
        ] + months + [
            "Total"
        ]
    )

else:

    income_table = pd.pivot_table(
        income_df,
        index="category",
        columns="Month",
        values="amount",
        aggfunc="sum",
        fill_value=0
    )

    # Ensure all 12 months exist
    income_table = income_table.reindex(
        columns=range(1, 13),
        fill_value=0
    )

    income_table.columns = months

    # Category total
    income_table["Total"] = (
        income_table.sum(axis=1)
    )

    # Total Income row
    income_table.loc[
        "Total Income"
    ] = income_table.sum(axis=0)

    income_table = (
        income_table
        .reset_index()
        .rename(
            columns={
                "category": "Category"
            }
        )
    )


st.dataframe(
    income_table,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# 💸 EXPENSE
# ============================================================

st.subheader("💸 Expense")


expense_df = year_df[
    expense_mask
].copy()


if expense_df.empty:

    expense_table = pd.DataFrame(
        columns=[
            "Category"
        ] + months + [
            "Total"
        ]
    )

else:

    expense_table = pd.pivot_table(
        expense_df,
        index="category",
        columns="Month",
        values="amount",
        aggfunc="sum",
        fill_value=0
    )

    # Ensure all 12 months exist
    expense_table = expense_table.reindex(
        columns=range(1, 13),
        fill_value=0
    )

    expense_table.columns = months

    # Category total
    expense_table["Total"] = (
        expense_table.sum(axis=1)
    )

    # Total Expense row
    expense_table.loc[
        "Total Expense"
    ] = expense_table.sum(axis=0)

    expense_table = (
        expense_table
        .reset_index()
        .rename(
            columns={
                "category": "Category"
            }
        )
    )


st.dataframe(
    expense_table,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# 🏦 YEAR SUMMARY
# ============================================================

st.subheader("🏦 Year Summary")


monthly_income = (
    income_df
    .groupby("Month")["amount"]
    .sum()
    if not income_df.empty
    else pd.Series(dtype=float)
)


monthly_expense = (
    expense_df
    .groupby("Month")["amount"]
    .sum()
    if not expense_df.empty
    else pd.Series(dtype=float)
)


summary = pd.DataFrame(
    index=[
        "Income",
        "Expense",
        "Balance"
    ],
    columns=months,
    dtype=float
)


for month_number in range(1, 13):

    month_name = months[
        month_number - 1
    ]

    income_value = monthly_income.get(
        month_number,
        0
    )

    expense_value = monthly_expense.get(
        month_number,
        0
    )

    summary.loc[
        "Income",
        month_name
    ] = income_value

    summary.loc[
        "Expense",
        month_name
    ] = expense_value

    summary.loc[
        "Balance",
        month_name
    ] = (
        income_value -
        expense_value
    )


# Year Total
summary["Year Total"] = (
    summary.sum(axis=1)
)


summary = (
    summary
    .reset_index()
    .rename(
        columns={
            "index": "Type"
        }
    )
)


st.dataframe(
    summary,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# 📊 CHARTS
# ============================================================

st.subheader("📊 Charts")


# ------------------------------------------------------------
# Monthly Income vs Expense
# ------------------------------------------------------------

chart_data = summary[
    summary["Type"].isin(
        [
            "Income",
            "Expense"
        ]
    )
].copy()


chart_data = chart_data.melt(
    id_vars="Type",
    value_vars=months,
    var_name="Month",
    value_name="Amount"
)


fig_income_expense = px.bar(
    chart_data,
    x="Month",
    y="Amount",
    color="Type",
    barmode="group",
    title=(
        f"Monthly Income vs Expense - "
        f"{selected_year}"
    )
)


st.plotly_chart(
    fig_income_expense,
    use_container_width=True
)


# ------------------------------------------------------------
# Expense by Category
# ------------------------------------------------------------

if not expense_df.empty:

    category_expense = (
        expense_df
        .groupby("category")["amount"]
        .sum()
        .reset_index()
        .sort_values(
            "amount",
            ascending=False
        )
    )

    fig_category = px.pie(
        category_expense,
        names="category",
        values="amount",
        title=(
            f"Expense by Category - "
            f"{selected_year}"
        )
    )

    st.plotly_chart(
        fig_category,
        use_container_width=True
    )

else:

    st.info(
        "No expense data available "
        "for this year."
    )


# ============================================================
# 📤 EXCEL EXPORT
# ============================================================

st.subheader("📤 Excel Export")


def create_excel():

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        # ----------------------------------------
        # Income
        # ----------------------------------------

        income_table.to_excel(
            writer,
            sheet_name="Income",
            index=False
        )

        # ----------------------------------------
        # Expense
        # ----------------------------------------

        expense_table.to_excel(
            writer,
            sheet_name="Expense",
            index=False
        )

        # ----------------------------------------
        # Year Summary
        # ----------------------------------------

        summary.to_excel(
            writer,
            sheet_name="Year Summary",
            index=False
        )

    output.seek(0)

    return output


excel_file = create_excel()


st.download_button(
    label="📥 Download Yearly Report Excel",
    data=excel_file,
    file_name=(
        f"MoneyMate_Yearly_Report_"
        f"{selected_year}.xlsx"
    ),
    mime=(
        "application/vnd.openxmlformats-officedocument."
        "spreadsheetml.sheet"
    )
)
