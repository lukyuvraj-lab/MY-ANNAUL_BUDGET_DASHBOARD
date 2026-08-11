import streamlit as st
import pandas as pd
from datetime import date

from utils.supabase_client import supabase


# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="MoneyMate Budget",
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
# DEFAULT CATEGORIES
# =========================================================
DEFAULT_CATEGORIES = [
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
# USER SETTINGS
# =========================================================
try:
    metadata = user.user_metadata or {}
except Exception:
    metadata = {}


settings_categories = metadata.get(
    "custom_categories",
    DEFAULT_CATEGORIES
)

settings_currency = metadata.get(
    "currency",
    "₹ INR"
)

if not isinstance(settings_categories, list):
    settings_categories = DEFAULT_CATEGORIES.copy()

if not settings_categories:
    settings_categories = DEFAULT_CATEGORIES.copy()


# =========================================================
# CURRENCY SYMBOL
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
# TITLE
# =========================================================
st.title("💰 Budget")
st.caption(
    "Set and track your monthly category budgets"
)


# =========================================================
# SELECT MONTH
# =========================================================
selected_month = st.date_input(
    "📅 Select Month",
    value=date.today().replace(day=1),
    key="budget_month"
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
# SET / UPDATE BUDGET
# =========================================================
st.divider()
st.subheader("➕ Set Category Budget")

col1, col2 = st.columns(2)

with col1:
    category = st.selectbox(
        "Category",
        settings_categories,
        key="budget_category"
    )

with col2:
    budget_amount = st.number_input(
        "Monthly Budget",
        min_value=0.0,
        step=500.0,
        format="%.2f",
        key="budget_amount"
    )


if st.button(
    "💾 Save Budget",
    use_container_width=True,
    key="save_budget"
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

                (
                    supabase
                    .table("budgets")
                    .update({
                        "amount": budget_amount
                    })
                    .eq("id", budget_id)
                    .eq("user_id", user.id)
                    .execute()
                )

                st.success(
                    "✅ Budget updated successfully!"
                )

            else:

                (
                    supabase
                    .table("budgets")
                    .insert({
                        "user_id": user.id,
                        "category": category,
                        "amount": budget_amount,
                        "month": str(month_start)
                    })
                    .execute()
                )

                st.success(
                    "✅ Budget saved successfully!"
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
        budget_response.data or []
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
        transaction_response.data or []
    )

except Exception as e:

    st.error(
        f"Unable to load expenses: {e}"
    )
    st.stop()


# =========================================================
# CLEAN BUDGET DATA
# =========================================================
if not budget_df.empty:

    if "amount" in budget_df.columns:
        budget_df["amount"] = pd.to_numeric(
            budget_df["amount"],
            errors="coerce"
        ).fillna(0.0)

    if "category" not in budget_df.columns:
        budget_df["category"] = ""


# =========================================================
# CLEAN EXPENSE DATA
# =========================================================
if not expense_df.empty:

    if "amount" in expense_df.columns:
        expense_df["amount"] = (
            expense_df["amount"]
            .astype(str)
            .str.replace("₹", "", regex=False)
            .str.replace(",", "", regex=False)
            .str.strip()
        )

        expense_df["amount"] = pd.to_numeric(
            expense_df["amount"],
            errors="coerce"
        ).fillna(0.0)

    if "category" not in expense_df.columns:
        expense_df["category"] = ""


# =========================================================
# SPENDING BY CATEGORY
# =========================================================
if not expense_df.empty:

    spent_by_category = (
        expense_df
        .groupby("category")["amount"]
        .sum()
        .to_dict()
    )

else:
    spent_by_category = {}


# =========================================================
# NO BUDGET MESSAGE
# =========================================================
if budget_df.empty:

    st.divider()

    st.info(
        f"💡 No budgets are set for "
        f"{month_start.strftime('%B %Y')}."
    )

    st.caption(
        "Use the form above to create your first category budget."
    )

    st.stop()


# =========================================================
# CREATE SUMMARY DATA
# =========================================================
summary_data = []

for index, row in budget_df.iterrows():

    category_name = str(
        row.get("category", "")
    )

    budget = float(
        row.get("amount", 0)
    )

    actual = float(
        spent_by_category.get(
            category_name,
            0
        )
    )

    remaining = budget - actual

    if budget > 0:
        utilization = (
            actual / budget
        ) * 100
    else:
        utilization = 0

    if actual > budget:
        status = "🔴 Over Budget"

    elif utilization >= 80:
        status = "🟠 Near Limit"

    else:
        status = "🟢 On Track"

    summary_data.append({
        "ID": row.get("id"),
        "Category": category_name,
        "Budget": budget,
        "Actual": actual,
        "Remaining": remaining,
        "Utilization": utilization,
        "Status": status
    })


summary_df = pd.DataFrame(summary_data)


# =========================================================
# TOTALS
# =========================================================
total_budget = float(
    summary_df["Budget"].sum()
)

total_spent = float(
    summary_df["Actual"].sum()
)

total_remaining = (
    total_budget - total_spent
)

if total_budget > 0:
    total_utilization = (
        total_spent / total_budget
    ) * 100
else:
    total_utilization = 0


# =========================================================
# KPI CARDS
# =========================================================
st.divider()
st.subheader(
    f"📊 Budget Overview — {month_start.strftime('%B %Y')}"
)

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric(
        "Total Budget",
        money(total_budget)
    )

with k2:
    st.metric(
        "Total Spent",
        money(total_spent)
    )

with k3:
    st.metric(
        "Remaining",
        money(total_remaining)
    )

with k4:
    st.metric(
        "Used",
        f"{total_utilization:.1f}%"
    )


# =========================================================
# OVERALL PROGRESS
# =========================================================
st.write("### Overall Budget Usage")

progress_value = min(
    max(total_utilization / 100, 0),
    1
)

st.progress(progress_value)

if total_utilization > 100:
    st.error(
        f"🔴 Budget exceeded by "
        f"{money(abs(total_remaining))}"
    )

elif total_utilization >= 80:
    st.warning(
        f"⚠️ You have used "
        f"{total_utilization:.1f}% of your budget."
    )

else:
    st.success(
        f"✅ You have used "
        f"{total_utilization:.1f}% of your budget."
    )


# =========================================================
# BUDGET VS ACTUAL TABLE
# =========================================================
st.divider()
st.subheader("📊 Budget vs Actual")

display_df = summary_df.copy()

display_df["Budget"] = display_df["Budget"].apply(
    money
)

display_df["Actual"] = display_df["Actual"].apply(
    money
)

display_df["Remaining"] = display_df["Remaining"].apply(
    money
)

display_df["Utilization"] = display_df[
    "Utilization"
].apply(
    lambda x: f"{x:.1f}%"
)

display_df = display_df[
    [
        "Category",
        "Budget",
        "Actual",
        "Remaining",
        "Utilization",
        "Status"
    ]
]

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# CATEGORY PROGRESS
# =========================================================
st.divider()
st.subheader("📈 Category Budget Usage")

for _, row in summary_df.iterrows():

    category_name = row["Category"]
    budget = float(row["Budget"])
    actual = float(row["Actual"])
    utilization = float(row["Utilization"])

    st.write(
        f"**{category_name}** — "
        f"{money(actual)} / {money(budget)}"
    )

    st.progress(
        min(
            max(utilization / 100, 0),
            1
        )
    )

    if utilization > 100:
        st.error(
            f"🔴 Over budget by "
            f"{money(actual - budget)}"
        )

    elif utilization >= 80:
        st.warning(
            f"⚠️ {utilization:.1f}% used"
        )

    else:
        st.caption(
            f"🟢 {utilization:.1f}% used"
        )


# =========================================================
# EDIT BUDGET
# =========================================================
st.divider()
st.subheader("✏️ Edit Budget")

budget_ids = budget_df["id"].tolist()

selected_budget_id = st.selectbox(
    "Select Budget",
    budget_ids,
    key="edit_budget_id"
)

selected_budget_rows = budget_df[
    budget_df["id"] == selected_budget_id
]

if not selected_budget_rows.empty:

    selected_budget = (
        selected_budget_rows.iloc[0]
    )

    current_category = str(
        selected_budget.get(
            "category",
            ""
        )
    )

    if current_category in settings_categories:
        category_index = settings_categories.index(
            current_category
        )
    else:
        category_index = 0

    edit_category = st.selectbox(
        "Category",
        settings_categories,
        index=category_index,
        key="edit_budget_category"
    )

    edit_amount = st.number_input(
        "Budget Amount",
        min_value=0.0,
        value=float(
            selected_budget.get(
                "amount",
                0
            )
        ),
        step=500.0,
        format="%.2f",
        key="edit_budget_amount"
    )

    if st.button(
        "✏️ Update Budget",
        use_container_width=True,
        key="update_budget_button"
    ):

        if edit_amount <= 0:

            st.error(
                "Budget must be greater than 0."
            )

        else:

            try:

                (
                    supabase
                    .table("budgets")
                    .update({
                        "category": edit_category,
                        "amount": edit_amount
                    })
                    .eq("id", selected_budget_id)
                    .eq("user_id", user.id)
                    .execute()
                )

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
    budget_ids,
    key="delete_budget_id"
)

if st.button(
    "🗑️ Delete Selected Budget",
    use_container_width=True,
    key="delete_budget_button"
):

    try:

        (
            supabase
            .table("budgets")
            .delete()
            .eq("id", delete_budget_id)
            .eq("user_id", user.id)
            .execute()
        )

        st.success(
            "✅ Budget deleted successfully!"
        )

        st.rerun()

    except Exception as e:

        st.error(
            f"Delete failed: {e}"
    )
