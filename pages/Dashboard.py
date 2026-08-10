import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from utils.supabase_client import supabase

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="MoneyMate Dashboard",
    page_icon="💰",
    layout="wide"
)

# -------------------------------------------------
# LOGIN CHECK
# -------------------------------------------------
if "user" not in st.session_state:
    st.warning("Please log in first.")
    st.stop()

st.title("💰 MoneyMate Dashboard")
st.caption("Your clean financial overview")

# -------------------------------------------------
# 1. FETCH & PROCESS DATABASE DATA
# -------------------------------------------------
response = (
    supabase
    .table("transactions")
    .select("*")
    .order("date", desc=True)
    .execute()
)
df = pd.DataFrame(response.data)

# Calculate financial indicators
if not df.empty:
    income = df.loc[df["type"].str.lower() == "income", "amount"].sum()
    expense = df.loc[df["type"].str.lower() == "expense", "amount"].sum()
else:
    income, expense = 0.0, 0.0

balance = income - expense
savings_pct = (balance / income) * 100 if income > 0 else 0.0

# -------------------------------------------------
# 2. CORE PERFORMANCE METRICS (KPIs)
# -------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("💰 Total Income", f"₹{income:,.2f}")
c2.metric("💸 Total Expense", f"₹{expense:,.2f}")
c3.metric("🏦 Net Balance", f"₹{balance:,.2f}")
c4.metric("📊 Savings Rate", f"{savings_pct:.1f}%")

st.divider()

# -------------------------------------------------
# 3. EXPENSE BREAKDOWN BY CATEGORY
# -------------------------------------------------
st.subheader("🥧 Expense Breakdown by Category")

if not df.empty and not df[df["type"].str.lower() == "expense"].empty:
    expense_df = df[df["type"].str.lower() == "expense"].copy()
    
    category_expense = (
        expense_df
        .groupby("category", as_index=False)["amount"]
        .sum()
        .sort_values("amount", ascending=False)
    )

    chart_col, table_col = st.columns([3, 2])
    
    with chart_col:
        fig = px.pie(
            category_expense, 
            names="category", 
            values="amount", 
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=300)
        st.plotly_chart(fig, use_container_width=True)

    with table_col:
        st.dataframe(
            category_expense.rename(columns={"category": "Category", "amount": "Total Amount (₹)"}),
            use_container_width=True, 
            hide_index=True
        )
else:
    st.info("No expense data recorded yet to generate breakdown analytics.")

st.divider()

# -------------------------------------------------
# 4. ACTION CENTER: ADD TRANSACTIONS DIRECTLY TO SUPABASE
# -------------------------------------------------
st.subheader("⚡ Quick Actions")
action_tab1, action_tab2 = st.tabs(["💵 Record New Income", "💸 Record New Expense"])

# Record Income Tab
with action_tab1:
    with st.form("inc_form", clear_on_submit=True):
        inc_cols = st.columns(4)
        inc_amt = inc_cols[0].number_input("Amount (₹)", min_value=0.0, step=100.0, key="inc_a")
        inc_cat = inc_cols[1].selectbox("Category", ["Salary", "Business", "Freelance", "Investment", "Gift", "Other"], key="inc_c")
        inc_note = inc_cols[2].text_input("Note / Description", key="inc_n")
        inc_date = inc_cols[3].date_input("Date", key="inc_d")
        
                if st.form_submit_button("➕ Save Income Entry", use_container_width=True):
            if inc_amt <= 0:
                st.error("Please log an amount greater than ₹0.")
            else:
                try:
                    supabase.table("transactions").insert({
                        "date": str(inc_date),
                        "type": "Income",
                        "category": inc_cat,
                        "amount": float(inc_amt),
                        "note": inc_note
                    }).execute()
                    st.success("Income synced to Supabase successfully! 🎉")
                    st.rerun()
                except Exception as db_error:
                    st.error("❌ Database Write Failure!")
                    st.code(str(db_error)) # This prints the explicit field issue

# Record Expense Tab
with action_tab2:
    with st.form("exp_form", clear_on_submit=True):
        exp_cols = st.columns(4)
        exp_amt = exp_cols[0].number_input("Amount (₹)", min_value=0.0, step=100.0, key="exp_a")
        exp_cat = exp_cols[1].selectbox("Category", [
            "Food", "Travel", "Shopping", "Bills", "Education", "Entertainment",
            "Medical", "Rent", "Groceries", "Fuel", "Electricity", "Mobile Recharge",
            "Internet", "Subscriptions", "Clothing", "Household", "Insurance", "Other"
        ], key="exp_c")
        exp_note = exp_cols[2].text_input("Note / Description", key="exp_n")
        exp_date = exp_cols[3].date_input("Date", key="exp_d")
        
               if st.form_submit_button("➖ Save Expense Entry", use_container_width=True):
            if exp_amt <= 0:
                st.error("Please log an amount greater than ₹0.")
            else:
                try:
                    supabase.table("transactions").insert({
                        "date": str(exp_date),
                        "type": "Expense",
                        "category": exp_cat,
                        "amount": float(exp_amt),
                        "note": exp_note
                    }).execute()
                    st.success("Expense synced to Supabase successfully! 🛡️")
                    st.rerun()
                except Exception as db_error:
                    st.error("❌ Database Write Failure!")
                    st.code(str(db_error)) # This prints the explicit field issue

st.divider()

# -------------------------------------------------
# 5. ALL LIVE TRANSACTIONS HISTORY
# -------------------------------------------------
st.subheader("📋 Ledger History")

if not df.empty:
    display_columns = ["date", "type", "category", "amount", "note"]
    clean_history = df[display_columns].copy()
    
    st.dataframe(
        clean_history.rename(columns=str.title), 
        use_container_width=True, 
        hide_index=True
    )
else:
    st.info("No historical entries located inside your database ledger.")

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.caption(
    f"MoneyMate Dashboard • Live Connection Verified • "
    f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
)
