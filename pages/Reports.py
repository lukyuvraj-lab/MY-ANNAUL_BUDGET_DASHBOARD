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
    hide_index=True
)


# =========================================================
# MONTHLY INCOME VS EXPENSE CHART
# =========================================================
st.divider()

st.subheader(
    "📈 Monthly Income vs Expense"
)

chart_df = monthly_df.melt(
    id_vars=["Month"],
    value_vars=[
        "Income",
        "Expense"
    ],
    var_name="Type",
    value_name="Amount"
)


fig_monthly = px.bar(
    chart_df,
    x="Month",
    y="Amount",
    color="Type",
    barmode="group",
    title=f"{selected_year} Monthly Income vs Expense"
)

fig_monthly.update_layout(
    xaxis_title="Month",
    yaxis_title="Amount (₹)",
    legend_title="",
    hovermode="x unified"
)

st.plotly_chart(
    fig_monthly,
    use_container_width=True
)


# =========================================================
# EXPENSE BY CATEGORY
# =========================================================
st.divider()

st.subheader(
    "🥧 Expense by Category"
)

expense_year_df = year_df[
    year_df["type"] == "Expense"
]

if expense_year_df.empty:

    st.info(
        "No expenses recorded for this year."
    )

else:

    category_df = (
        expense_year_df
        .groupby("category")["amount"]
        .sum()
        .reset_index()
        .sort_values(
            "amount",
            ascending=False
        )
    )

    fig_category = px.pie(
        category_df,
        names="category",
        values="amount",
        title=f"{selected_year} Expense by Category",
        hole=0.35
    )

    st.plotly_chart(
        fig_category,
        use_container_width=True
    )


# =========================================================
# TRANSACTION SUMMARY
# =========================================================
st.divider()

st.subheader(
    "📋 Transactions for Selected Year"
)

year_display_df = year_df[
    [
        "date",
        "type",
        "amount",
        "category",
        "account",
        "note"
    ]
].copy()

year_display_df["date"] = (
    year_display_df["date"]
    .dt.strftime("%d-%m-%Y")
)

st.dataframe(
    year_display_df,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# EXCEL EXPORT
# =========================================================
st.divider()

st.subheader(
    "📤 Export Report"
)


def create_excel():

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        # Year summary
        summary_df = pd.DataFrame({
            "Metric": [
                "Year",
                "Total Income",
                "Total Expense",
                "Balance",
                "Savings %"
            ],
            "Value": [
                selected_year,
                income,
                expense,
                balance,
                savings
            ]
        })

        summary_df.to_excel(
            writer,
            sheet_name="Summary",
            index=False
        )

        # Month-wise report
        monthly_df.to_excel(
            writer,
            sheet_name="Monthly Report",
            index=False
        )

        # Category report
        if not expense_year_df.empty:

            category_df.to_excel(
                writer,
                sheet_name="Expense by Category",
                index=False
            )

        # Transactions
        year_df.to_excel(
            writer,
            sheet_name="Transactions",
            index=False
        )

    output.seek(0)

    return output


excel_file = create_excel()


st.download_button(
    label="📥 Download Excel Report",
    data=excel_file,
    file_name=f"MoneyMate_Report_{selected_year}.xlsx",
    mime=(
        "application/vnd.openxmlformats-officedocument."
        "spreadsheetml.sheet"
    ),
    use_container_width=True
    )
