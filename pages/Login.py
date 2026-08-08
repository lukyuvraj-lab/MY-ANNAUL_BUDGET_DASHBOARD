import streamlit as st
from supabase import create_client

# ============================================================
# SUPABASE
# ============================================================

SUPABASE_URL = "https://wkelsfwfdecgqibeolnk.supabase.co"

SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndrZWxzZndmZGVjZ3FpYmVvbG5rIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODU3NjExOTYsImV4cCI6MjEwMTM"

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="MoneyMate Login",
    page_icon="🔐"
)

# ============================================================
# LOGIN PAGE
# ============================================================

st.title("🔐 MoneyMate Login")

email = st.text_input("Email")

password = st.text_input(
    "Password",
    type="password"
)

col1, col2 = st.columns(2)

# ============================================================
# LOGIN
# ============================================================

with col1:

    if st.button("Login", use_container_width=True):

        if not email or not password:

            st.warning(
                "Please enter email and password."
            )

        else:

            try:

                response = supabase.auth.sign_in_with_password(
                    {
                        "email": email,
                        "password": password
                    }
                )

                # Save logged-in user
                st.session_state["user"] = response.user

                st.success("Login successful!")

                # Go to Dashboard
                st.switch_page(
                    "pages/Dashboard.py"
                )

            except Exception as e:

                st.error(
                    f"Login failed: {e}"
                )


# ============================================================
# SIGN UP
# ============================================================

with col2:

    if st.button("Sign Up", use_container_width=True):

        if not email or not password:

            st.warning(
                "Please enter email and password."
            )

        else:

            try:

                response = supabase.auth.sign_up(
                    {
                        "email": email,
                        "password": password
                    }
                )

                st.success(
                    "Account created successfully! "
                    "Please check your email."
                )

            except Exception as e:

                st.error(
                    f"Sign Up failed: {e}"
            )
    st.subheader("📊 Financial Summary")

    if transactions:
        st.dataframe(
            transactions[::-1],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info(
            "No transactions yet. "
            "Add income or expense from the menu."
        )

# ============================================================
# ADD INCOME
# ============================================================

elif menu == "Add Income":

    st.title("💵 Add Income")

    with st.form("income_form"):

        amount = st.number_input(
            "Amount (₹)",
            min_value=0.0,
            step=100.0
        )

        category = st.selectbox(
            "Category",
            [
                "Salary",
                "Business",
                "Freelance",
                "Investment",
                "Gift",
                "Other"
            ]
        )

        description = st.text_input(
            "Description"
        )

        date = st.date_input(
            "Date"
        )

        submit = st.form_submit_button(
            "➕ Add Income"
        )

        if submit:

            if amount <= 0:
                st.error("Enter a valid amount.")
            else:

                st.session_state["transactions"].append({
                    "Date": str(date),
                    "Type": "Income",
                    "Category": category,
                    "Description": description,
                    "Amount": float(amount)
                })

                st.success("Income added successfully! ✅")

                st.rerun()

# ============================================================
# ADD EXPENSE
# ============================================================

elif menu == "Add Expense":

    st.title("💸 Add Expense")

    with st.form("expense_form"):

        amount = st.number_input(
            "Amount (₹)",
            min_value=0.0,
            step=100.0
        )

        category = st.selectbox(
            "Category",
            [
                "Food",
                "Travel",
                "Shopping",
                "Bills",
                "Education",
                "Entertainment",
                "Medical",
                "Rent",
                "Other"
            ]
        )

        description = st.text_input(
            "Description"
        )

        date = st.date_input(
            "Date"
        )

        submit = st.form_submit_button(
            "➖ Add Expense"
        )

        if submit:

            if amount <= 0:
                st.error("Enter a valid amount.")
            else:

                st.session_state["transactions"].append({
                    "Date": str(date),
                    "Type": "Expense",
                    "Category": category,
                    "Description": description,
                    "Amount": float(amount)
                })

                st.success("Expense added successfully! ✅")

                st.rerun()

# ============================================================
# TRANSACTIONS
# ============================================================

elif menu == "Transactions":

    st.title("📋 Transactions")

    if transactions:

        st.dataframe(
            transactions[::-1],
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")

        if st.button("🗑️ Clear All Transactions"):

            st.session_state["transactions"] = []

            st.success("Transactions cleared.")

            st.rerun()

    else:

        st.info("No transactions available.")

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    f"MoneyMate • "
    f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
    )                st.error(
                    f"Sign Up failed: {e}"
                )import streamlit as st
from supabase import create_client

# ============================================================
# SUPABASE
# ============================================================

SUPABASE_URL = "https://wkelsfwfdecgqibeolnk.supabase.co"

SUPABASE_KEY = "YOUR_SUPABASE_ANON_KEY"

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="MoneyMate Login",
    page_icon="🔐"
)

# ============================================================
# LOGIN PAGE
# ============================================================

st.title("🔐 MoneyMate Login")

email = st.text_input("Email")

password = st.text_input(
    "Password",
    type="password"
)

col1, col2 = st.columns(2)

# ============================================================
# LOGIN
# ============================================================

with col1:

    if st.button("Login", use_container_width=True):

        if not email or not password:

            st.warning(
                "Please enter email and password."
            )

        else:

            try:

                response = supabase.auth.sign_in_with_password(
                    {
                        "email": email,
                        "password": password
                    }
                )

                # Save logged-in user
                st.session_state["user"] = response.user

                st.success("Login successful!")

                # Go to Dashboard
                st.switch_page(
                    "pages/Dashboard.py"
                )

            except Exception as e:

                st.error(
                    f"Login failed: {e}"
                )


# ============================================================
# SIGN UP
# ============================================================

with col2:

    if st.button("Sign Up", use_container_width=True):

        if not email or not password:

            st.warning(
                "Please enter email and password."
            )

        else:

            try:

                response = supabase.auth.sign_up(
                    {
                        "email": email,
                        "password": password
                    }
                )

                st.success(
                    "Account created successfully! "
                    "Please check your email."
                )

            except Exception as e:

                st.error(
                    f"Sign Up failed: {e}"
                )
