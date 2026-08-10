import streamlit as st
from utils.supabase_client import supabase


# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="MoneyMate Settings",
    page_icon="⚙️",
    layout="wide"
)


# =========================================================
# RESTORE SUPABASE SESSION
# =========================================================
if "access_token" in st.session_state and "refresh_token" in st.session_state:
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
# DEFAULT SETTINGS
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

DEFAULT_ACCOUNTS = [
    "Cash",
    "Bank",
    "UPI",
    "Credit Card"
]

DEFAULT_CURRENCY = "₹ INR"


# =========================================================
# LOAD USER METADATA
# =========================================================
try:
    user_metadata = user.user_metadata or {}
except Exception:
    user_metadata = {}


saved_name = user_metadata.get("display_name", "")
saved_currency = user_metadata.get("currency", DEFAULT_CURRENCY)
saved_categories = user_metadata.get(
    "custom_categories",
    DEFAULT_CATEGORIES
)
saved_accounts = user_metadata.get(
    "custom_accounts",
    DEFAULT_ACCOUNTS
)


# Safety checks
if not isinstance(saved_categories, list):
    saved_categories = DEFAULT_CATEGORIES.copy()

if not isinstance(saved_accounts, list):
    saved_accounts = DEFAULT_ACCOUNTS.copy()


# =========================================================
# SESSION STATE
# =========================================================
if "settings_categories" not in st.session_state:
    st.session_state["settings_categories"] = saved_categories.copy()

if "settings_accounts" not in st.session_state:
    st.session_state["settings_accounts"] = saved_accounts.copy()


# =========================================================
# HELPER: SAVE USER METADATA
# =========================================================
def save_user_settings(
    display_name=None,
    currency=None,
    categories=None,
    accounts=None
):
    current_metadata = dict(user_metadata)

    if display_name is not None:
        current_metadata["display_name"] = display_name.strip()

    if currency is not None:
        current_metadata["currency"] = currency

    if categories is not None:
        current_metadata["custom_categories"] = categories

    if accounts is not None:
        current_metadata["custom_accounts"] = accounts

    try:
        response = supabase.auth.update_user({
            "data": current_metadata
        })

        # Update local session user metadata
        try:
            updated_user = response.user

            if updated_user:
                st.session_state["user"] = updated_user
        except Exception:
            pass

        return True, None

    except Exception as e:
        return False, str(e)


# =========================================================
# TITLE
# =========================================================
st.title("⚙️ Settings")
st.caption("Manage your MoneyMate profile, currency, categories and accounts.")


# =========================================================
# PROFILE
# =========================================================
st.divider()
st.subheader("👤 Profile")

col1, col2 = st.columns(2)

with col1:
    email = getattr(user, "email", None)

    st.text_input(
        "Email",
        value=email or "",
        disabled=True
    )

with col2:
    display_name = st.text_input(
        "Display Name",
        value=saved_name,
        placeholder="Enter your name",
        key="display_name_input"
    )

if st.button(
    "💾 Save Profile",
    use_container_width=True,
    key="save_profile"
):
    success, error = save_user_settings(
        display_name=display_name
    )

    if success:
        st.success("✅ Profile updated successfully.")
        st.rerun()
    else:
        st.error(f"Unable to update profile: {error}")


# =========================================================
# CURRENCY
# =========================================================
st.divider()
st.subheader("💰 Currency")

currency_options = [
    "₹ INR",
    "$ USD",
    "€ EUR",
    "£ GBP",
    "¥ JPY",
    "₩ KRW",
    "AED",
    "SGD"
]

if saved_currency not in currency_options:
    saved_currency = DEFAULT_CURRENCY

selected_currency = st.selectbox(
    "Default Currency",
    currency_options,
    index=currency_options.index(saved_currency),
    key="currency_select"
)

if st.button(
    "💾 Save Currency",
    use_container_width=True,
    key="save_currency"
):
    success, error = save_user_settings(
        currency=selected_currency
    )

    if success:
        st.success("✅ Currency updated.")
        st.rerun()
    else:
        st.error(f"Unable to save currency: {error}")


# =========================================================
# CATEGORIES
# =========================================================
st.divider()
st.subheader("🏷️ Categories")
st.caption("Add your own expense or income categories.")

category_col1, category_col2 = st.columns([2, 1])

with category_col1:
    new_category = st.text_input(
        "New Category",
        placeholder="Example: Gym",
        key="new_category"
    )

with category_col2:
    category_type = st.selectbox(
        "Type",
        ["Expense", "Income"],
        key="category_type"
    )

if st.button(
    "➕ Add Category",
    use_container_width=True,
    key="add_category"
):
    cleaned_category = new_category.strip()

    if not cleaned_category:
        st.error("Please enter a category name.")

    elif cleaned_category.lower() in [
        x.lower()
        for x in st.session_state["settings_categories"]
    ]:
        st.warning("This category already exists.")

    else:
        st.session_state["settings_categories"].append(
            cleaned_category
        )

        success, error = save_user_settings(
            categories=st.session_state["settings_categories"]
        )

        if success:
            st.success(
                f"✅ {category_type} category '{cleaned_category}' added."
            )
            st.rerun()
        else:
            st.error(f"Unable to save category: {error}")


# Display categories
categories = st.session_state["settings_categories"]

if categories:
    st.write("### Current Categories")

    category_data = [
        {
            "No.": i,
            "Category": category
        }
        for i, category in enumerate(categories, start=1)
    ]

    st.dataframe(
        category_data,
        use_container_width=True,
        hide_index=True
    )

    delete_category = st.selectbox(
        "Select Category to Delete",
        categories,
        key="delete_category_select"
    )

    if st.button(
        "🗑️ Delete Category",
        use_container_width=True,
        key="delete_category"
    ):
        if len(categories) <= 1:
            st.error("At least one category must remain.")
        else:
            updated_categories = [
                category
                for category in categories
                if category != delete_category
            ]

            success, error = save_user_settings(
                categories=updated_categories
            )

            if success:
                st.session_state["settings_categories"] = (
                    updated_categories
                )

                st.success(
                    f"✅ Category '{delete_category}' deleted."
                )
                st.rerun()
            else:
                st.error(
                    f"Unable to delete category: {error}"
                )


# =========================================================
# ACCOUNTS
# =========================================================
st.divider()
st.subheader("🏦 Accounts")
st.caption("Manage the accounts you use for transactions.")

account_col1, account_col2 = st.columns([2, 1])

with account_col1:
    new_account = st.text_input(
        "New Account",
        placeholder="Example: SBI Bank",
        key="new_account"
    )

with account_col2:
    account_type = st.selectbox(
        "Account Type",
        [
            "Bank",
            "Cash",
            "UPI",
            "Credit Card",
            "Savings",
            "Other"
        ],
        key="account_type"
    )

if st.button(
    "➕ Add Account",
    use_container_width=True,
    key="add_account"
):
    cleaned_account = new_account.strip()

    if not cleaned_account:
        st.error("Please enter an account name.")

    elif cleaned_account.lower() in [
        x.lower()
        for x in st.session_state["settings_accounts"]
    ]:
        st.warning("This account already exists.")

    else:
        st.session_state["settings_accounts"].append(
            cleaned_account
        )

        success, error = save_user_settings(
            accounts=st.session_state["settings_accounts"]
        )

        if success:
            st.success(
                f"✅ {account_type} account '{cleaned_account}' added."
            )
            st.rerun()
        else:
            st.error(f"Unable to save account: {error}")


accounts = st.session_state["settings_accounts"]

if accounts:
    st.write("### Current Accounts")

    account_data = [
        {
            "No.": i,
            "Account": account
        }
        for i, account in enumerate(accounts, start=1)
    ]

    st.dataframe(
        account_data,
        use_container_width=True,
        hide_index=True
    )

    delete_account = st.selectbox(
        "Select Account to Delete",
        accounts,
        key="delete_account_select"
    )

    if st.button(
        "🗑️ Delete Account",
        use_container_width=True,
        key="delete_account"
    ):
        if len(accounts) <= 1:
            st.error("At least one account must remain.")
        else:
            updated_accounts = [
                account
                for account in accounts
                if account != delete_account
            ]

            success, error = save_user_settings(
                accounts=updated_accounts
            )

            if success:
                st.session_state["settings_accounts"] = (
                    updated_accounts
                )

                st.success(
                    f"✅ Account '{delete_account}' deleted."
                )
                st.rerun()
            else:
                st.error(
                    f"Unable to delete account: {error}"
                )


# =========================================================
# NOTIFICATION PREFERENCES
# =========================================================
st.divider()
st.subheader("🔔 Notifications")

st.info(
    "These preferences are saved to your MoneyMate profile. "
    "Actual notification delivery can be added later."
)

budget_alert = st.checkbox(
    "🔔 Budget exceeded alert",
    value=bool(
        user_metadata.get(
            "budget_alert",
            True
        )
    ),
    key="budget_alert"
)

budget_warning = st.checkbox(
    "⚠️ Budget nearing limit alert",
    value=bool(
        user_metadata.get(
            "budget_warning",
            True
        )
    ),
    key="budget_warning"
)

monthly_summary = st.checkbox(
    "📊 Monthly financial summary",
    value=bool(
        user_metadata.get(
            "monthly_summary",
            True
        )
    ),
    key="monthly_summary"
)

if st.button(
    "💾 Save Notification Settings",
    use_container_width=True,
    key="save_notifications"
):
    current_metadata = dict(user_metadata)

    current_metadata["budget_alert"] = budget_alert
    current_metadata["budget_warning"] = budget_warning
    current_metadata["monthly_summary"] = monthly_summary

    try:
        response = supabase.auth.update_user({
            "data": current_metadata
        })

        try:
            if response.user:
                st.session_state["user"] = response.user
        except Exception:
            pass

        st.success("✅ Notification preferences saved.")
        st.rerun()

    except Exception as e:
        st.error(
            f"Unable to save notification settings: {e}"
        )


# =========================================================
# PASSWORD
# =========================================================
st.divider()
st.subheader("🔐 Security")

st.caption(
    "You can request a password reset email for your account."
)

if st.button(
    "📧 Send Password Reset Email",
    use_container_width=True,
    key="password_reset"
):
    if not email:
        st.error("No email address is available for this account.")
    else:
        try:
            supabase.auth.reset_password_for_email(
                email
            )

            st.success(
                "✅ Password reset email sent. "
                "Please check your email."
            )

        except Exception as e:
            st.error(
                f"Unable to send password reset email: {e}"
            )


# =========================================================
# DATA / ACCOUNT INFORMATION
# =========================================================
st.divider()
st.subheader("📊 Account Information")

info_col1, info_col2, info_col3 = st.columns(3)

with info_col1:
    st.metric(
        "Categories",
        len(st.session_state["settings_categories"])
    )

with info_col2:
    st.metric(
        "Accounts",
        len(st.session_state["settings_accounts"])
    )

with info_col3:
    st.metric(
        "Currency",
        selected_currency
    )


# =========================================================
# LOGOUT
# =========================================================
st.divider()
st.subheader("🚪 Account")

if st.button(
    "🚪 Logout",
    use_container_width=True,
    key="logout_button"
):
    try:
        supabase.auth.sign_out()
    except Exception:
        pass

    # Clear login/session information
    keys_to_remove = [
        "user",
        "access_token",
        "refresh_token",
        "settings_categories",
        "settings_accounts"
    ]

    for key in keys_to_remove:
        st.session_state.pop(key, None)

    st.success("Logged out successfully.")
    st.switch_page("pages/Login.py")
