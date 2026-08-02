import streamlit as st
import pandas as pd

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
else:
    st.info("Please upload your budget Excel file.")
    st.stop()

# ==========================================
# Input and Output Files
# ==========================================
INPUT_FILE = "Annual_Budget.xlsx"      # Your source data
OUTPUT_FILE = "Annual_Budget_Dashboard.xlsx"

# ==========================================
# Read Data
# ==========================================
df = pd.read_excel(INPUT_FILE)

# Ensure Date column is datetime
df["Date"] = pd.to_datetime(df["Date"])

# Extract Month
df["Month"] = df["Date"].dt.strftime("%b")

# ==========================================
# Summary Calculations
# ==========================================
total_budget = df["Budget"].sum()
total_actual = df["Actual"].sum()
remaining = total_budget - total_actual

utilization = (
    (total_actual / total_budget) * 100
    if total_budget > 0 else 0
)

# ==========================================
# Monthly Summary
# ==========================================
monthly = (
    df.groupby("Month")[["Budget", "Actual"]]
      .sum()
      .reindex(
          ["Jan","Feb","Mar","Apr","May","Jun",
           "Jul","Aug","Sep","Oct","Nov","Dec"]
      )
      .fillna(0)
)

# ==========================================
# Category Summary
# ==========================================
category = (
    df.groupby("Category")[["Budget", "Actual"]]
      .sum()
      .sort_values("Actual", ascending=False)
)

# ==========================================
# Write Excel
# ==========================================
with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:

    df.to_excel(writer, sheet_name="Data", index=False)

    monthly.to_excel(writer, sheet_name="Monthly Summary")

    category.to_excel(writer, sheet_name="Category Summary")

    summary = pd.DataFrame({
        "Metric": [
            "Total Budget",
            "Total Actual",
            "Remaining Budget",
            "Budget Utilization (%)"
        ],
        "Value": [
            total_budget,
            total_actual,
            remaining,
            round(utilization, 2)
        ]
    })

    summary.to_excel(writer, sheet_name="Dashboard", index=False)

# ==========================================
# Formatting
# ==========================================
wb = load_workbook(OUTPUT_FILE)
ws = wb["Dashboard"]

header_fill = PatternFill(
    start_color="1F4E78",
    end_color="1F4E78",
    fill_type="solid"
)

for cell in ws[1]:
    cell.font = Font(bold=True, color="FFFFFF")
    cell.fill = header_fill

wb.save(OUTPUT_FILE)

print("Dashboard created successfully!")
