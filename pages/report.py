import streamlit as st
import pandas as pd
from io import BytesIO
from pathlib import Path
from copy import copy

from openpyxl import load_workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.chart.shapes import GraphicalProperties


# ============================================================
# REPORT PAGE
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

required_columns = ["date", "amount", "type", "category"]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    st.error(
        "Missing columns in transactions table: "
        + ", ".join(missing_columns)
    )
    st.stop()


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

df["type"] = (
    df["type"]
    .fillna("")
    .astype(str)
    .str.strip()
)

df["category"] = (
    df["category"]
    .fillna("Other")
    .astype(str)
    .str.strip()
)

df.loc[
    df["category"] == "",
    "category"
] = "Other"

df = df.dropna(subset=["date"])

if df.empty:
    st.info("No valid transactions found.")
    st.stop()


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
    st.warning("No transactions found for the selected year.")
    st.stop()


months = [
    "Jan", "Feb", "Mar", "Apr",
    "May", "Jun", "Jul", "Aug",
    "Sep", "Oct", "Nov", "Dec"
]

year_df["Month"] = year_df["date"].dt.month

income_df = year_df[
    year_df["type"].str.lower() == "income"
].copy()

expense_df = year_df[
    year_df["type"].str.lower() == "expense"
].copy()

total_income = float(income_df["amount"].sum())
total_expense = float(expense_df["amount"].sum())
total_balance = total_income - total_expense

spend_percent = (
    (total_expense / total_income) * 100
    if total_income > 0
    else 0
)


# ============================================================
# BUILD TABLES
# ============================================================

def make_month_table(source):
    if source.empty:
        return pd.DataFrame(
            columns=["Item"] + months
        )

    result = pd.pivot_table(
        source,
        index="category",
        columns="Month",
        values="amount",
        aggfunc="sum",
        fill_value=0
    )

    result = result.reindex(
        columns=range(1, 13),
        fill_value=0
    )

    result.columns = months
    result = result.reset_index()
    result = result.rename(
        columns={"category": "Item"}
    )

    return result


income_table = make_month_table(income_df)
expense_table = make_month_table(expense_df)


# ============================================================
# STREAMLIT SUMMARY
# ============================================================

st.subheader(f"📅 {selected_year} Overview")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("💰 Total Income", f"₹{total_income:,.2f}")

with c2:
    st.metric("💸 Total Expense", f"₹{total_expense:,.2f}")

with c3:
    st.metric("🏦 Balance", f"₹{total_balance:,.2f}")

with c4:
    st.metric("📊 Spend %", f"{spend_percent:.2f}%")

st.divider()

st.subheader("💰 Income")
st.dataframe(
    income_table,
    use_container_width=True,
    hide_index=True
)

st.subheader("💸 Expense")
st.dataframe(
    expense_table,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# EXCEL TEMPLATE REPORT
# ============================================================

def copy_row_style(ws, source_row, target_row, max_col=14):
    """Copy the exact formatting of a template row."""
    if source_row == target_row:
        return

    ws.row_dimensions[target_row].height = (
        ws.row_dimensions[source_row].height
    )

    for col in range(1, max_col + 1):
        source = ws.cell(source_row, col)
        target = ws.cell(target_row, col)

        if source.has_style:
            target._style = copy(source._style)

        if source.number_format:
            target.number_format = source.number_format

        target.font = copy(source.font)
        target.fill = copy(source.fill)
        target.border = copy(source.border)
        target.alignment = copy(source.alignment)
        target.protection = copy(source.protection)


def clear_row(ws, row, max_col=14):
    for col in range(1, max_col + 1):
        ws.cell(row, col).value = None


def create_excel_report():
    # --------------------------------------------------------
    # IMPORTANT:
    # Put this file in the SAME folder as report.py:
    #
    # MoneyMate_Annual_Budget_Template.xlsx
    #
    # This is the sanitized copy of your uploaded template.
    # The password sheet is NOT included.
    # --------------------------------------------------------

    template_path = (
        Path(__file__).resolve().parent
        / "MoneyMate_Annual_Budget_Template.xlsx"
    )

    if not template_path.exists():
        raise FileNotFoundError(
            "MoneyMate_Annual_Budget_Template.xlsx was not found. "
            "Upload/copy the template file into the same folder as report.py."
        )

    wb = load_workbook(template_path)

    # Keep exactly ONE sheet.
    for sheet_name in list(wb.sheetnames):
        if sheet_name != "Budget by month":
            del wb[sheet_name]

    ws = wb["Budget by month"]

    # Remove old tables because their formulas refer to sample data.
    for table_name in list(ws.tables.keys()):
        del ws.tables[table_name]

    # Remove old charts. We recreate them using the live report data.

    # --------------------------------------------------------
    # YEAR TITLE
    # --------------------------------------------------------

    ws["A2"] = "ANNUAL BUDGET"

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    ws["B5"] = total_income
    ws["B6"] = total_expense
    ws["B8"] = total_balance
    ws["B10"] = spend_percent / 100

    ws["B5"].number_format = '#,##0'
    ws["B6"].number_format = '#,##0'
    ws["B8"].number_format = '#,##0'
    ws["B10"].number_format = '0.00%'

    # --------------------------------------------------------
    # INCOME - TEMPLATE ROWS 14:18
    # --------------------------------------------------------

    income_start = 14
    income_capacity = 5
    income_total_row = 19

    income_categories = (
        income_table["Item"].tolist()
        if not income_table.empty
        else []
    )

    # If there are more than the template's 5 income rows,
    # insert extra rows immediately before Total.
    if len(income_categories) > income_capacity:
        extra = len(income_categories) - income_capacity

        for _ in range(extra):
            ws.insert_rows(income_total_row)

        for r in range(
            income_total_row,
            income_total_row + extra
        ):
            copy_row_style(
                ws,
                income_start + income_capacity - 1,
                r
            )

        income_total_row += extra

    # If fewer than 5 categories, hide unused template rows.
    for index in range(income_capacity):
        row = income_start + index
        clear_row(ws, row)

        if index >= len(income_categories):
            ws.row_dimensions[row].hidden = True
        else:
            ws.row_dimensions[row].hidden = False

    # Fill income categories and months.
    for index, category in enumerate(income_categories):
        row = income_start + index

        # Restore alternating template styles.
        source_style_row = (
            14 if index % 2 == 0 else 15
        )
        copy_row_style(
            ws,
            source_style_row,
            row
        )

        ws.cell(row, 1).value = category

        row_data = income_table[
            income_table["Item"] == category
        ].iloc[0]

        for month_index, month in enumerate(
            months,
            start=2
        ):
            value = float(row_data[month])
            ws.cell(row, month_index).value = (
                value if value != 0 else None
            )
            ws.cell(
                row,
                month_index
            ).number_format = '#,##0.00'

        ws.cell(
            row,
            14
        ).value = (
            f"=SUM(B{row}:M{row})"
        )
        ws.cell(
            row,
            14
        ).number_format = '#,##0.00'

    # Total row.
    for col in range(1, 15):
        if col == 1:
            ws.cell(
                income_total_row,
                col
            ).value = "Total"
        else:
            letter = chr(64 + col)
            ws.cell(
                income_total_row,
                col
            ).value = (
                f"=SUM({letter}{income_start}:"
                f"{letter}{income_total_row - 1})"
            )
            ws.cell(
                income_total_row,
                col
            ).number_format = '#,##0.00'

    # Unhide total.
    ws.row_dimensions[income_total_row].hidden = False

    # --------------------------------------------------------
    # FIND EXPENSE SECTION AFTER INCOME ROW CHANGES
    # --------------------------------------------------------

    expense_title_row = None

    for row in range(1, ws.max_row + 1):
        if ws.cell(row, 1).value == "EXPENSES":
            expense_title_row = row
            break

    if expense_title_row is None:
        raise ValueError("EXPENSES section not found in template.")

    expense_header_row = expense_title_row + 1
    expense_start = expense_header_row + 1

    # Template originally has 22 expense rows.
    expense_capacity = 22

    # Current total row is found by scanning after expense header.
    expense_total_row = None

    for row in range(
        expense_start,
        ws.max_row + 1
    ):
        if ws.cell(row, 1).value == "Total":
            expense_total_row = row
            break

    if expense_total_row is None:
        raise ValueError("Expense Total row not found in template.")

    expense_categories = (
        expense_table["Item"].tolist()
        if not expense_table.empty
        else []
    )

    # Insert rows if required.
    current_capacity = expense_total_row - expense_start

    if len(expense_categories) > current_capacity:
        extra = (
            len(expense_categories)
            - current_capacity
        )

        for _ in range(extra):
            ws.insert_rows(expense_total_row)

        for r in range(
            expense_total_row,
            expense_total_row + extra
        ):
            copy_row_style(
                ws,
                expense_start,
                r
            )

        expense_total_row += extra
        current_capacity += extra

    # Clear/hide unused rows.
    for index in range(current_capacity):
        row = expense_start + index
        clear_row(ws, row)

        if index >= len(expense_categories):
            ws.row_dimensions[row].hidden = True
        else:
            ws.row_dimensions[row].hidden = False

    # Fill expense rows.
    for index, category in enumerate(expense_categories):
        row = expense_start + index

        # Template alternates row styles.
        source_style_row = (
            expense_start
            if index % 2 == 0
            else expense_start + 1
        )

        copy_row_style(
            ws,
            source_style_row,
            row
        )

        ws.cell(row, 1).value = category

        row_data = expense_table[
            expense_table["Item"] == category
        ].iloc[0]

        for month_index, month in enumerate(
            months,
            start=2
        ):
            value = float(row_data[month])

            ws.cell(row, month_index).value = (
                value if value != 0 else None
            )

            ws.cell(
                row,
                month_index
            ).number_format = '#,##0.00'

        ws.cell(
            row,
            14
        ).value = (
            f"=SUM(B{row}:M{row})"
        )

        ws.cell(
            row,
            14
        ).number_format = '#,##0.00'

    # Expense total.
    for col in range(1, 15):
        if col == 1:
            ws.cell(
                expense_total_row,
                col
            ).value = "Total"
        else:
            letter = chr(64 + col)

            ws.cell(
                expense_total_row,
                col
            ).value = (
                f"=SUM({letter}{expense_start}:"
                f"{letter}{expense_total_row - 1})"
            )

            ws.cell(
                expense_total_row,
                col
            ).number_format = '#,##0.00'

    ws.row_dimensions[expense_total_row].hidden = False

    # --------------------------------------------------------
    # BALANCE ROW
    # --------------------------------------------------------

    balance_row = expense_total_row + 2

    # The template already has the balance row at this location
    # after any inserted expense rows. Restore its style from the
    # original balance style if necessary.
    if balance_row > ws.max_row:
        ws.insert_rows(balance_row)

    ws.cell(
        balance_row,
        1
    ).value = "BALANCE"

    for col in range(2, 14):
        letter = chr(64 + col)

        ws.cell(
            balance_row,
            col
        ).value = (
            f"={letter}{income_total_row}-"
            f"{letter}{expense_total_row}"
        )

        ws.cell(
            balance_row,
            col
        ).number_format = '#,##0.00'

    ws.cell(
        balance_row,
        14
    ).value = (
        f"=N{income_total_row}-"
        f"N{expense_total_row}"
    )

    ws.cell(
        balance_row,
        14
    ).number_format = '#,##0.00'

    # --------------------------------------------------------
    # CHARTS
    # --------------------------------------------------------
    #
    # Keep the original charts from the supplied Excel template.
    # The template charts render reliably in Excel/mobile Excel.
    # We only replace their source ranges with live numeric data.

    chart_data_start = balance_row + 40

    # Top summary chart source
    ws.cell(chart_data_start, 1).value = "Summary"
    ws.cell(chart_data_start + 1, 1).value = "Total Income"
    ws.cell(chart_data_start + 2, 1).value = "Total Expense"
    ws.cell(chart_data_start + 1, 2).value = float(total_income)
    ws.cell(chart_data_start + 2, 2).value = float(total_expense)

    # Monthly chart source
    monthly_source_row = chart_data_start + 5
    ws.cell(monthly_source_row, 1).value = "Type"

    for col, month in enumerate(months, start=2):
        ws.cell(monthly_source_row, col).value = month

    ws.cell(monthly_source_row + 1, 1).value = "INCOME"
    ws.cell(monthly_source_row + 2, 1).value = "EXPENSES"

    for month_number in range(1, 13):
        ws.cell(
            monthly_source_row + 1,
            month_number + 1
        ).value = float(monthly_income.get(month_number, 0))

        ws.cell(
            monthly_source_row + 2,
            month_number + 1
        ).value = float(monthly_expense.get(month_number, 0))

    # Expense category chart source
    category_source_row = chart_data_start + 9
    ws.cell(category_source_row, 1).value = "Expense Category"
    ws.cell(category_source_row, 2).value = "Amount"

    for index, category in enumerate(expense_categories):
        row = category_source_row + index + 1
        ws.cell(row, 1).value = category
        value = float(
            expense_table.loc[
                expense_table["Item"] == category,
                "Total"
            ].iloc[0]
        )
        ws.cell(row, 2).value = value

    # --------------------------------------------------------
    # UPDATE TEMPLATE CHARTS
    # --------------------------------------------------------

    from openpyxl.chart.data_source import AxDataSource, NumRef, StrRef

    if len(ws._charts) >= 3:
        monthly_chart = ws._charts[0]
        category_chart = ws._charts[1]
        top_chart = ws._charts[2]

        # Top summary chart: Income + Expense
        if len(top_chart.ser) >= 1:
            top_chart.ser[0].val.numRef.f = (
                f"'Budget by month'!$B${chart_data_start + 1}:"
                f"$B${chart_data_start + 2}"
            )
            top_chart.ser[0].cat = AxDataSource(
                strRef=StrRef(
                    f"'Budget by month'!$A${chart_data_start + 1}:"
                    f"$A${chart_data_start + 2}"
                )
            )

        # Monthly Income vs Expense
        if len(monthly_chart.ser) >= 2:
            monthly_chart.ser[0].val.numRef.f = (
                f"'Budget by month'!$B${monthly_source_row + 1}:"
                f"$M${monthly_source_row + 1}"
            )
            monthly_chart.ser[1].val.numRef.f = (
                f"'Budget by month'!$B${monthly_source_row + 2}:"
                f"$M${monthly_source_row + 2}"
            )

            monthly_cat = AxDataSource(
                numRef=NumRef(
                    f"'Budget by month'!$B${monthly_source_row}:"
                    f"$M${monthly_source_row}"
                )
            )
            monthly_chart.ser[0].cat = monthly_cat
            monthly_chart.ser[1].cat = monthly_cat

        # Expense category
        if expense_categories and len(category_chart.ser) >= 1:
            last_row = (
                category_source_row +
                len(expense_categories)
            )

            category_chart.ser[0].val.numRef.f = (
                f"'Budget by month'!$B${category_source_row + 1}:"
                f"$B${last_row}"
            )

            category_chart.ser[0].cat = AxDataSource(
                strRef=StrRef(
                    f"'Budget by month'!$A${category_source_row + 1}:"
                    f"$A${last_row}"
                )
            )

        # Keep the same visual sizes as the supplied template.
        top_chart.width = 15
        top_chart.height = 7.5

        monthly_chart.width = 15
        monthly_chart.height = 7.5

        category_chart.width = 15
        category_chart.height = 7.5

        # Place charts below the balance row.
        top_chart.anchor = "F4"
        monthly_chart.anchor = f"A{balance_row + 3}"
        category_chart.anchor = f"K{balance_row + 3}"

    # --------------------------------------------------------
    # PRINT / VIEW SETTINGS

    # --------------------------------------------------------

    ws.sheet_view.showGridLines = False
    ws.freeze_panes = None

    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0

    ws.sheet_properties.pageSetUpPr.fitToPage = True

    # Include the full visible report, including charts.
    ws.print_area = (
        f"A1:V{balance_row + 30}"
    )

    # Force Excel to calculate formulas when opened.
    try:
        wb.calculation.fullCalcOnLoad = True
        wb.calculation.forceFullCalc = True
        wb.calculation.calcMode = "auto"
    except Exception:
        pass

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return output


# ============================================================
# DOWNLOAD
# ============================================================

st.subheader("📤 Excel Report")

try:
    excel_file = create_excel_report()

    st.download_button(
        label="📥 Download Annual Budget Report",
        data=excel_file,
        file_name=(
            f"MoneyMate_Annual_Budget_"
            f"{selected_year}.xlsx"
        ),
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )

except Exception as e:
    st.error(
        f"Unable to create Excel report: {e}"
    )
