import streamlit as st
import pandas as pd
from pathlib import Path
from io import BytesIO
from copy import copy

from openpyxl import load_workbook
from openpyxl.chart import BarChart, Reference


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="MoneyMate - Reports",
    page_icon="📊",
    layout="wide"
)

st.title("📊 MoneyMate - Yearly Report")


# ============================================================
# CATEGORY LIST
# EXACTLY FROM Transactions.py
# ============================================================

income_categories = [
    "Salary",
    "Business",
    "Interest",
    "Balance Last Year",
    "Chit Fund",
    "Freelance",
    "Bouns",
    "Invesment",
    "Rental",
    "Refunds",
    "Commission",
    "Sales",
    "Tax Refunds",
    "Other Income"
]

expense_categories = [
    "Food & Dining",
    "Travel",
    "Transportation",
    "Shopping",
    "Housing",
    "Utilities",
    "Healthcare",
    "Education",
    "Emi/Loan",
    "Insurance",
    "Personal Care",
    "Family",
    "Bills",
    "Taxes",
    "Charity",
    "Bakery",
    "Beating",
    "Bike Maintenance",
    "Bills",
    "Business Invesment",
    "Chit Fund",
    "Entertainment",
    "Gifts",
    "Groceries/vegetable's",
    "Investment",
    "Home",
    "Employee Salaries",
    "Fuel",
    "Rent",
    "Subscriptions",
    "Recharge",
    "Mobile",
    "Taxes",
    "Interest",
    "Other Expense"
]

months = [
    "Jan", "Feb", "Mar", "Apr",
    "May", "Jun", "Jul", "Aug",
    "Sep", "Oct", "Nov", "Dec"
]


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
    st.stop()


if not data:
    st.info("No transactions found.")
    st.stop()


df = pd.DataFrame(data)


# ============================================================
# PREPARE DATA
# ============================================================

required_columns = [
    "date",
    "amount",
    "type",
    "category"
]

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
    .str.lower()
)

df["category"] = (
    df["category"]
    .fillna("Other Expense")
    .astype(str)
    .str.strip()
)

df = df.dropna(
    subset=["date"]
)

if df.empty:
    st.info("No valid transactions found.")
    st.stop()

df["Month"] = df["date"].dt.month


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
    st.warning(
        "No transactions found for the selected year."
    )
    st.stop()


# ============================================================
# INCOME / EXPENSE
# ============================================================

income_df = year_df[
    year_df["type"] == "income"
].copy()

expense_df = year_df[
    year_df["type"] == "expense"
].copy()


total_income = income_df["amount"].sum()
total_expense = expense_df["amount"].sum()
total_balance = total_income - total_expense

spend_percent = (
    (total_expense / total_income) * 100
    if total_income > 0
    else 0
)


# ============================================================
# STREAMLIT KPI
# ============================================================

st.subheader(
    f"📅 {selected_year} Overview"
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "💰 Total Income",
        f"₹{total_income:,.2f}"
    )

with col2:
    st.metric(
        "💸 Total Expense",
        f"₹{total_expense:,.2f}"
    )

with col3:
    st.metric(
        "🏦 Balance",
        f"₹{total_balance:,.2f}"
    )

with col4:
    st.metric(
        "📊 Spend %",
        f"{spend_percent:.2f}%"
    )


st.divider()


# ============================================================
# BUILD REPORT TABLES
# USE EXACT CATEGORY LIST
# ============================================================

def build_category_table(source_df, categories):
    """
    Creates a table using the exact category order from
    Transactions.py.

    Categories with no transactions remain in the report
    with zero values.
    """

    result = pd.DataFrame(
        0.0,
        index=categories,
        columns=months
    )

    if not source_df.empty:
        grouped = (
            source_df
            .groupby(
                ["category", "Month"]
            )["amount"]
            .sum()
        )

        for category in categories:
            if category not in grouped.index.get_level_values(
                "category"
            ):
                continue

            for month_number in range(1, 13):

                try:
                    value = grouped.loc[
                        (category, month_number)
                    ]
                except KeyError:
                    value = 0

                result.loc[
                    category,
                    months[month_number - 1]
                ] = float(value)

    result.index.name = "Item"

    result["Total"] = result.sum(axis=1)

    result = result.reset_index()

    return result


income_table = build_category_table(
    income_df,
    income_categories
)

expense_table = build_category_table(
    expense_df,
    expense_categories
)


# ============================================================
# STREAMLIT TABLES
# ============================================================

st.subheader("💰 Income")

st.dataframe(
    income_table,
    use_container_width=True,
    hide_index=True
)

st.subheader("💸 Expenses")

st.dataframe(
    expense_table,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# MONTHLY SUMMARY
# ============================================================

monthly_income = []
monthly_expense = []
monthly_balance = []

for month_number in range(1, 13):

    income_value = income_df.loc[
        income_df["Month"] == month_number,
        "amount"
    ].sum()

    expense_value = expense_df.loc[
        expense_df["Month"] == month_number,
        "amount"
    ].sum()

    monthly_income.append(
        float(income_value)
    )

    monthly_expense.append(
        float(expense_value)
    )

    monthly_balance.append(
        float(
            income_value - expense_value
        )
    )


summary = pd.DataFrame({
    "Type": [
        "Income",
        "Expense",
        "Balance"
    ]
})

for i, month in enumerate(months):

    summary[month] = [
        monthly_income[i],
        monthly_expense[i],
        monthly_balance[i]
    ]

summary["Year Total"] = [
    total_income,
    total_expense,
    total_balance
]


st.subheader("🏦 Year Summary")

st.dataframe(
    summary,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# TEMPLATE LOCATION
# ============================================================

BASE_DIR = Path(
    __file__
).resolve().parent

TEMPLATE_NAME = (
    "MoneyMate_Annual_Budget_Template.xlsx"
)

TEMPLATE_PATH = (
    BASE_DIR /
    TEMPLATE_NAME
)


# ============================================================
# FIND TEMPLATE
# ============================================================

template_path = None

possible_paths = [
    BASE_DIR / TEMPLATE_NAME,
    Path.cwd() / TEMPLATE_NAME,
    Path("/mount/src/value-pending") / TEMPLATE_NAME,
]

for path in possible_paths:
    if path.exists() and path.is_file():
        template_path = path
        break


# ============================================================
# TEMPLATE STATUS
# ============================================================

with st.expander(
    "🔧 Excel Template Status"
):

    st.write(
        "report.py folder:",
        str(BASE_DIR)
    )

    st.write(
        "Template expected:",
        str(BASE_DIR / TEMPLATE_NAME)
    )

    if template_path:
        st.success(
            f"Template found: {template_path}"
        )
    else:
        st.error(
            "Template not found."
        )


# ============================================================
# HELPER
# ============================================================

def find_text_cell(ws, text):
    text = str(text).strip().lower()

    for row in ws.iter_rows():
        for cell in row:

            if cell.value is None:
                continue

            value = str(
                cell.value
            ).strip().lower()

            if value == text:
                return cell

    return None


def find_month_header_row(ws):
    for row in ws.iter_rows():

        values = {
            str(cell.value).strip()
            for cell in row
            if cell.value is not None
        }

        count = sum(
            month in values
            for month in months
        )

        if count >= 8:
            return row[0].row

    return None


def find_month_columns(ws, header_row):
    month_columns = {}

    if header_row is None:
        return month_columns

    for cell in ws[header_row]:

        if cell.value is None:
            continue

        value = str(
            cell.value
        ).strip()

        if value in months:
            month_columns[
                value
            ] = cell.column

    return month_columns


def copy_row_style(ws, source_row, target_row):
    for col in range(
        1,
        ws.max_column + 1
    ):
        source = ws.cell(
            source_row,
            col
        )
        target = ws.cell(
            target_row,
            col
        )

        if source.has_style:
            target._style = copy(
                source._style
            )

        if source.number_format:
            target.number_format = (
                source.number_format
            )

        if source.alignment:
            target.alignment = copy(
                source.alignment
            )

        if source.font:
            target.font = copy(
                source.font
            )

        if source.fill:
            target.fill = copy(
                source.fill
            )

        if source.border:
            target.border = copy(
                source.border
            )


# ============================================================
# CREATE EXCEL REPORT
# ============================================================

def create_excel_report():

    if template_path is None:
        raise FileNotFoundError(
            "MoneyMate_Annual_Budget_Template.xlsx "
            "was not found.\n\n"
            f"Expected location:\n{BASE_DIR / TEMPLATE_NAME}\n\n"
            "Upload the template to the same GitHub folder "
            "as report.py."
        )


    # --------------------------------------------------------
    # LOAD TEMPLATE
    # --------------------------------------------------------

    wb = load_workbook(
        filename=str(template_path)
    )


    # --------------------------------------------------------
    # USE FIRST SHEET ONLY
    # --------------------------------------------------------

    ws = wb.worksheets[0]

    ws.title = "Budget by month"


    # --------------------------------------------------------
    # NO FREEZE PANES
    # --------------------------------------------------------

    ws.freeze_panes = None


    # --------------------------------------------------------
    # REMOVE ALL OTHER SHEETS
    # --------------------------------------------------------

    for sheet in wb.worksheets[1:]:
        wb.remove(sheet)


    # --------------------------------------------------------
    # FIND TEMPLATE SECTIONS
    # --------------------------------------------------------

    income_cell = find_text_cell(
        ws,
        "Income"
    )

    expense_cell = find_text_cell(
        ws,
        "Expenses"
    )

    if expense_cell is None:
        expense_cell = find_text_cell(
            ws,
            "Expense"
        )

    header_row = find_month_header_row(
        ws
    )

    month_columns = find_month_columns(
        ws,
        header_row
    )


    # --------------------------------------------------------
    # FALLBACK MONTH COLUMNS
    # --------------------------------------------------------

    if len(month_columns) < 12:

        header_row = (
            header_row
            if header_row is not None
            else 13
        )

        month_columns = {
            month: index
            for index, month in enumerate(
                months,
                start=2
            )
        }


    # --------------------------------------------------------
    # ITEM COLUMN
    # --------------------------------------------------------

    item_column = 1


    # --------------------------------------------------------
    # FIND DATA START
    # --------------------------------------------------------

    if income_cell:
        income_start_row = (
            income_cell.row + 2
        )
    else:
        income_start_row = (
            header_row + 1
        )


    if expense_cell:
        expense_start_row = (
            expense_cell.row + 2
        )
    else:
        expense_start_row = (
            income_start_row +
            len(income_categories) +
            5
        )


    # --------------------------------------------------------
    # WRITE CATEGORY TABLE
    # --------------------------------------------------------

    def write_table(
        table,
        categories,
        start_row
    ):

        # Template's category rows are used first.
        # Extra rows copy the style from the last
        # available row.

        current_row = start_row

        for category_index, category in enumerate(
            categories
        ):

            if current_row > ws.max_row:

                copy_row_style(
                    ws,
                    current_row - 1,
                    current_row
                )

            ws.cell(
                current_row,
                item_column
            ).value = category

            row_data = table[
                table["Item"] == category
            ]

            if row_data.empty:
                row_data = None
            else:
                row_data = row_data.iloc[0]

            for month in months:

                col = month_columns[
                    month
                ]

                value = (
                    0
                    if row_data is None
                    else float(
                        row_data[month]
                    )
                )

                ws.cell(
                    current_row,
                    col
                ).value = value

            current_row += 1

        # Total row

        total_row = current_row

        ws.cell(
            total_row,
            item_column
        ).value = "Total"

        for month in months:

            col = month_columns[
                month
            ]

            ws.cell(
                total_row,
                col
            ).value = sum(
                float(
                    table.loc[
                        table["Item"] == category,
                        month
                    ].iloc[0]
                )
                if not table.loc[
                    table["Item"] == category,
                    month
                ].empty
                else 0
                for category in categories
            )

        # Copy total-row style from nearest
        # template total row if available.

        return total_row


    income_total_row = write_table(
        income_table,
        income_categories,
        income_start_row
    )


    expense_total_row = write_table(
        expense_table,
        expense_categories,
        expense_start_row
    )


    # --------------------------------------------------------
    # SUMMARY VALUES
    # --------------------------------------------------------

    summary_values = {
        "total monthly income": total_income,
        "total income": total_income,
        "total monthly expenses": total_expense,
        "total expenses": total_expense,
        "balance": total_balance,
        "percentage of income spent": spend_percent,
    }


    for row in ws.iter_rows():

        for cell in row:

            if cell.value is None:
                continue

            label = str(
                cell.value
            ).strip().lower()

            if label in summary_values:

                target = ws.cell(
                    cell.row,
                    cell.column + 1
                )

                target.value = (
                    summary_values[label]
                )

                if (
                    "percentage"
                    in label
                ):
                    target.number_format = (
                        '0.00"%"'
                    )
                else:
                    target.number_format = (
                        '#,##0.00'
                    )


    # --------------------------------------------------------
    # YEAR IN TITLE
    # --------------------------------------------------------

    for row in ws.iter_rows():

        for cell in row:

            if isinstance(
                cell.value,
                str
            ):

                for old_year in [
                    "2024",
                    "2025",
                    "2026"
                ]:

                    if old_year in cell.value:

                        cell.value = (
                            cell.value.replace(
                                old_year,
                                str(selected_year)
                            )
                        )


    # ========================================================
    # CHART DATA
    # ========================================================

    # Keep chart data far to the right.
    # These columns are hidden.

    chart_col = 30
    chart_row = 2

    ws.cell(
        chart_row,
        chart_col
    ).value = "Month"

    ws.cell(
        chart_row,
        chart_col + 1
    ).value = "Income"

    ws.cell(
        chart_row,
        chart_col + 2
    ).value = "Expense"


    for index, month in enumerate(
        months,
        start=1
    ):

        row = chart_row + index

        ws.cell(
            row,
            chart_col
        ).value = month

        ws.cell(
            row,
            chart_col + 1
        ).value = monthly_income[
            index - 1
        ]

        ws.cell(
            row,
            chart_col + 2
        ).value = monthly_expense[
            index - 1
        ]


    # --------------------------------------------------------
    # REMOVE EXISTING BROKEN CHARTS
    # --------------------------------------------------------

    ws._charts = []


    # --------------------------------------------------------
    # CREATE WORKING BAR CHART
    # --------------------------------------------------------

    chart = BarChart()

    chart.type = "col"

    chart.style = 10

    chart.title = (
        f"Monthly Income vs Expense - "
        f"{selected_year}"
    )

    chart.y_axis.title = "Amount"

    chart.x_axis.title = "Month"

    chart.height = 8

    chart.width = 16


    data_reference = Reference(
        ws,
        min_col=chart_col + 1,
        max_col=chart_col + 2,
        min_row=chart_row,
        max_row=chart_row + 12
    )

    category_reference = Reference(
        ws,
        min_col=chart_col,
        min_row=chart_row + 1,
        max_row=chart_row + 12
    )


    chart.add_data(
        data_reference,
        titles_from_data=True
    )

    chart.set_categories(
        category_reference
    )

    chart.legend.position = "b"


    # --------------------------------------------------------
    # CHART LOCATION
    # --------------------------------------------------------

    chart_row_visible = max(
        expense_total_row + 4,
        38
    )

    ws.add_chart(
        chart,
        f"A{chart_row_visible}"
    )


    # ========================================================
    # HIDE CHART DATA
    # ========================================================

    for col_number in range(
        chart_col,
        chart_col + 3
    ):

        column_letter = ""

        number = col_number

        while number > 0:

            number, remainder = divmod(
                number - 1,
                26
            )

            column_letter = (
                chr(65 + remainder)
                + column_letter
            )

        ws.column_dimensions[
            column_letter
        ].hidden = True


    # ========================================================
    # EXCEL SETTINGS
    # ========================================================

    ws.freeze_panes = None

    ws.sheet_view.showGridLines = False

    ws.sheet_properties.pageSetUpPr.fitToPage = True

    ws.page_setup.fitToWidth = 1

    ws.page_setup.fitToHeight = 0

    ws.page_setup.orientation = "landscape"


    # ========================================================
    # SAVE
    # ========================================================

    output = BytesIO()

    wb.save(output)

    output.seek(0)

    return output


# ============================================================
# DOWNLOAD
# ============================================================

st.divider()

st.subheader(
    "📤 Download Excel Report"
)


if template_path is None:

    st.error(
        "❌ Excel template not found."
    )

    st.code(
        str(
            BASE_DIR /
            TEMPLATE_NAME
        )
    )

    st.info(
        "Upload MoneyMate_Annual_Budget_Template.xlsx "
        "to the SAME GitHub folder as report.py."
    )

else:

    try:

        excel_file = (
            create_excel_report()
        )

        st.download_button(
            label=(
                "📥 Download Annual "
                "Budget Report"
            ),
            data=excel_file,
            file_name=(
                f"MoneyMate_Annual_Budget_"
                f"{selected_year}.xlsx"
            ),
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            use_container_width=True
        )

        st.success(
            "✅ Annual Budget Excel report is ready."
        )

    except Exception as e:

        st.error(
            "Unable to create Excel report."
        )

        st.exception(e)

