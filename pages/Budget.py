import streamlit as st
import pandas as pd
from datetime import date

from utils.supabase_client import supabase

# =========================================================
# RESTORE SUPABASE LOGIN SESSION
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
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="MoneyMate Budget",
    page_icon="💰",
    layout="wide"
)


# =========================================================
# LOGIN CHECK
# =========================================================
if "user" not in st.session_state:
    st.warning("Please log in first.")
    st.stop()

user = st.session_state["user"]


# =========================================================
# CATEGORY LIST
# =========================================================
categories = [
    "Bakery",
    "Beating",
    "Bike",
    "Bills",
    "Chiti",
    "Credit Card",
    "Entertainment",
    "Education",
    "Electricity",
    "EMI",
    "Gifts",
    "Groceries/vegetable's",
    "Investment",
    "Medical",
    "Home",
    "Hotel/Dhaba",
    "Insurance",
    "Internet",
    "Loan",
    "Fuel",
    "Rent",
    "Recharge",
    "Saloon",
    "Shopping",
    "Subscriptions",
    "Shop",
    "Travel",
    "Transport",
    "Trip",
    "Mobile",
    "Utensils",
    "Other"
]


# =========================================================
# TITLE
# =========================================================
st.title("💰 Budget")
st.caption("Set and track your monthly category budgets")


# =========================================================
# SELECT MONTH
# =========================================================
selected_month = st.date_input(
    "📅 Select Month",
    value=date.today().replace(day=1)
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
# SET BUDGET
# =========================================================
st.divider()

st.subheader("➕ Set Category Budget")

col1, col2 = st.columns(2)

with col1:

    category = st.selectbox(
        "Category",
        categories
    )

with col2:

    budget_amount = st.number_input(
        "Monthly Budget",
        min_value=0.0,
        step=500.0
    )


# =========================================================
# SAVE BUDGET
# =========================================================
if st.button(
    "💾 Save Budget",
    use_container_width=True
):

    if budget_amount <= 0:

        st.error(
            "Budget must be greater than 0."
        )

    else:

        try:

            existing = (
                supabase
                .table("budgets")
                .select("*")
                .eq("user_id", user.id)
                .eq("category", category)
                .eq("month", str(month_start))
                .execute()
            )

            if existing.data:

                budget_id = existing.data[0]["id"]

                supabase.table("budgets").update({
                    "amount": budget_amount
                }).eq(
                    "id",
                    budget_id
                ).eq(
                    "user_id",
                    user.id
                ).execute()

                st.success(
                    "✅ Budget updated!"
                )

            else:

                supabase.table("budgets").insert({
                    "user_id": user.id,
                    "category": category,
                    "amount": budget_amount,
                    "month": str(month_start)
                }).execute()

                st.success(
                    "✅ Budget saved!"
                )

            st.rerun()

        except Exception as e:

            st.error(
                f"Unable to save budget: {e}"
            )


# =========================================================
# LOAD BUDGETS
# =========================================================
try:

    budget_response = (
        supabase
        .table("budgets")
        .select("*")
        .eq("user_id", user.id)
        .eq("month", str(month_start))
        .execute()
    )

    budget_df = pd.DataFrame(
        budget_response.data
    )

except Exception as e:

    st.error(
        f"Unable to load budgets: {e}"
    )

    st.stop()


# =========================================================
# LOAD EXPENSES
# =========================================================
try:

    transaction_response = (
        supabase
        .table("transactions")
        .select("*")
        .eq("user_id", user.id)
        .eq("type", "Expense")
        .gte("date", str(month_start))
        .lt("date", str(next_month))
        .execute()
    )

    expense_df = pd.DataFrame(
        transaction_response.data
    )

except Exception as e:

    st.error(
        f"Unable to load expenses: {e}"
    )

    st.stop()


# =========================================================
# BUDGET OVERVIEW
# =========================================================
if budget_df.empty:

    st.info(
        "💡 No budgets set for this month yet."
    )

    st.stop()


if not expense_df.empty:

    expense_df["amount"] = pd.to_numeric(
        expense_df["amount"],
        errors="coerce"
    ).fillna(0)

    spent_by_category = (
        expense_df
        .groupby("category")["amount"]
        .sum()
        .to_dict()
    )

else:

    spent_by_category = {}


# =========================================================
# TOTALS
# =========================================================
total_budget = 0
total_spent = 0

for _, row in budget_df.iterrows():

    budget = float(row["amount"])

    spent = float(
        spent_by_category.get(
            row["category"],
            0
        )
    )

    total_budget += budget
    total_spent += spent


total_remaining = (
    total_budget - total_spent
)


# =========================================================
# BUDGET VS ACTUAL SPENDING
# =========================================================
st.divider()

st.subheader("📊 Budget vs Actual")

summary_data = []

for index, (_, row) in enumerate(budget_df.iterrows(), start=1):

    category_name = row["category"]

    budget = float(row["amount"])

    actual = float(
        spent_by_category.get(
            category_name,
            0
        )
    )

    remaining = budget - actual

    summary_data.append({
        "Budget No.": index,
        "Category": category_name,
        "Budget": f"₹{budget:,.0f}",
        "Actual": f"₹{actual:,.0f}",
        "Remaining": f"₹{remaining:,.0f}"
    })


summary_df = pd.DataFrame(summary_data)

st.dataframe(
    summary_df,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# EDIT BUDGET
# =========================================================
st.divider()

st.subheader("✏️ Edit Budget")

budget_options = budget_df["id"].tolist()

selected_budget_id = st.selectbox(
    "Select Budget",
    budget_options,
    key="edit_budget_id"
)

selected_budget = budget_df[
    budget_df["id"] == selected_budget_id
].iloc[0]

edit_category = st.selectbox(
    "Category",
    categories,
    index=(
        categories.index(selected_budget["category"])
        if selected_budget["category"] in categories
        else 0
    ),
    key="edit_budget_category"
)

edit_amount = st.number_input(
    "Budget Amount",
    min_value=0.0,
    value=float(selected_budget["amount"]),
    step=500.0,
    key="edit_budget_amount"
)

if st.button(
    "✏️ Update Budget",
    use_container_width=True,
    key="update_budget_button"
):

    if edit_amount <= 0:

        st.error("Budget must be greater than 0.")

    else:

        try:

            supabase.table("budgets").update({
                "category": edit_category,
                "amount": edit_amount
            }).eq(
                "id",
                selected_budget_id
            ).eq(
                "user_id",
                user.id
            ).execute()

            st.success(
                "✅ Budget updated successfully!"
            )

            st.rerun()

        except Exception as e:

            st.error(
                f"Update failed: {e}"
            )


# =========================================================
# DELETE BUDGET
# =========================================================
st.divider()

st.subheader("🗑️ Delete Budget")

delete_budget_id = st.selectbox(
    "Select Budget to Delete",
    budget_options,
    key="delete_budget_id"
)

if st.button(
    "🗑️ Delete Selected Budget",
    use_container_width=True,
    key="delete_budget_button"
):

    try:

        supabase.table("budgets") \
            .delete() \
            .eq("id", delete_budget_id) \
            .eq("user_id", user.id) \
            .execute()

        st.success(
            "✅ Budget deleted successfully!"
        )

        st.rerun()

    except Exception as e:

        st.error(
            f"Delete failed: {e}"
        )
