from openpyxl import load_workbook
import pandas as pd
import streamlit as st
import re

st.set_page_config(page_title="Annual Budget Dashboard", layout="wide")

uploaded_file = st.file_uploader(
    "Upload Annual Budget Excel",
    type=["xlsx"]
)

if uploaded_file is None:
    st.stop()

wb = load_workbook(uploaded_file, data_only=True)


# --------------------------
# Convert any cell to number
# --------------------------
def to_number(value):

    if value is None:
        return 0

    if isinstance(value, (int, float)):
        return float(value)

    value = str(value)

    value = re.sub(r"[^\d.-]", "", value)

    if value == "":
        return 0

    try:
        return float(value)
    except:
        return 0


# ==========================
# MONTHLY
# ==========================

ws = wb["Budget by month"]

monthly_income = to_number(ws["B5"].value)
monthly_expense = to_number(ws["B6"].value)

monthly_saving = monthly_income - monthly_expense

monthly_spend_pct = (
    monthly_expense / monthly_income * 100
    if monthly_income else 0
)

monthly_saving_pct = (
    monthly_saving / monthly_income * 100
    if monthly_income else 0
)

st.subheader("Monthly Summary")

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Income", f"₹{monthly_income:,.0f}")
c2.metric("Expense", f"₹{monthly_expense:,.0f}")
c3.metric("Saving", f"₹{monthly_saving:,.0f}")
c4.metric("Spend %", f"{monthly_spend_pct:.1f}%")
c5.metric("Saving %", f"{monthly_saving_pct:.1f}%")


# ==========================
# YEARLY
# ==========================

ys = wb[" Budget by year"]

yearly_income = to_number(ys["B5"].value)
yearly_expense = to_number(ys["B6"].value)

yearly_saving = yearly_income - yearly_expense

st.subheader("Yearly Summary")

st.write("Income :", yearly_income)
st.write("Expense :", yearly_expense)
st.write("Saving :", yearly_saving)


# ==========================
# YEAR TABLE
# ==========================

rows = []

r = 4

while True:

    year = ys[f"V{r}"].value

    if year is None:
        break

    rows.append([
        year,
        to_number(ys[f"W{r}"].value),
        to_number(ys[f"X{r}"].value),
        to_number(ys[f"Y{r}"].value),
        to_number(ys[f"Z{r}"].value)
    ])

    r += 1

year_df = pd.DataFrame(
    rows,
    columns=[
        "Year",
        "Income",
        "Expense",
        "Saving",
        "Spend %"
    ]
)

st.dataframe(year_df, use_container_width=True)
