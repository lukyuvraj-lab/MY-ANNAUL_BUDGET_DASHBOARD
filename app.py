from openpyxl import load_workbook
import pandas as pd

wb = load_workbook("My Annual Budget(1).xlsx", data_only=True)

# ---------- Monthly ----------
ws = wb["Budget by month"]

monthly_income = ws["B5"].value
monthly_expense = ws["B6"].value
monthly_saving = monthly_income - monthly_expense
monthly_spend_pct = monthly_expense / monthly_income * 100
monthly_saving_pct = monthly_saving / monthly_income * 100

print(monthly_income)
print(monthly_expense)
print(monthly_saving)

# ---------- Yearly ----------
ys = wb[" Budget by year"]

yearly_income = ys["B5"].value
yearly_expense = ys["B6"].value
yearly_saving = yearly_income - yearly_expense

print(yearly_income)
print(yearly_expense)
print(yearly_saving)

# ---------- Year Table ----------
rows = []

r = 4

while True:

    year = ys[f"V{r}"].value

    if year is None:
        break

    income = ys[f"W{r}"].value
    expense = ys[f"X{r}"].value
    saving = ys[f"Y{r}"].value
    percent = ys[f"Z{r}"].value

    rows.append(
        [year, income, expense, saving, percent]
    )

    r += 1

year_df = pd.DataFrame(
    rows,
    columns=[
        "Year",
        "Income",
        "Expenses",
        "Savings",
        "Spend %"
    ]
)

print(year_df)
