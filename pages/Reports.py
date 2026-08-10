import streamlit as st
import pandas as pd
from io import BytesIO
from pathlib import Path
from openpyxl import load_workbook
from openpyxl.chart import BarChart, Reference


# ============================================================
# PAGE
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
    st.stop()


if not data:
    st.info("No transactions found.")
    st.stop()


df = pd.DataFrame(data)


# ============================================================
# CHECK COLUMNS
# ============================================================

required_columns = [
    "date",
    "amount",
    "type",
    "category"
]

missing = [
    col
    for col in required_columns
    if col not in df.columns
]

if missing:
    st.error(
        "Missing columns: "
        + ", ".join(missing)
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
    .str.lower()
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

df = df.dropna(
    subset=["date"]
)

if df.empty:
    st.info("No valid transactions found.")
    st.stop()


# ============================================================
# YEAR
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

year_df["month_number"] = (
    year_df["date"].dt.month
)


# ============================================================
# MONTHS
# ============================================================

months = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec"
]


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

balance = (
    total_income -
    total_expense
)

if total_income:
    spend_percent = (
        total_expense /
        total_income
    ) * 100
else:
    spend_percent = 0


# ============================================================
# STREAMLIT SUMMARY
# ============================================================

st.subheader(
    f"📅 {selected_year} Overview"
)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "💰 Total Income",
        f"₹{total_income:,.2f}"
    )

with c2:
    st.metric(
        "💸 Total Expense",
        f"₹{total_expense:,.2f}"
    )

with c3:
    st.metric(
        "🏦 Balance",
        f"₹{balance:,.2f}"
    )

with c4:
    st.metric(
        "📊 Spend %",
        f"{spend_percent:.2f}%"
    )


# ============================================================
# CREATE MONTHLY CATEGORY DATA
# ============================================================

def create_category_table(source):

    if source.empty:
        return pd.DataFrame(
            columns=[
                "Item"
            ] + months + [
                "Total"
            ]
        )

    table = pd.pivot_table(
        source,
        index="category",
        columns="month_number",
        values="amount",
        aggfunc="sum",
        fill_value=0
    )

    table = table.reindex(
        columns=range(1, 13),
        fill_value=0
    )

    table.columns = months

    table = table.reset_index()

    table = table.rename(
        columns={
            "category": "Item"
        }
    )

    table["Total"] = (
        table[months]
        .sum(axis=1)
    )

    return table


income_table = create_category_table(
    income_df
)

expense_table = create_category_table(
    expense_df
)


# ============================================================
# SHOW TABLES
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
# MONTHLY TOTALS
# ============================================================

monthly_income = []

monthly_expense = []

monthly_balance = []

for month_number in range(1, 13):

    inc = income_df.loc[
        income_df["month_number"] == month_number,
        "amount"
    ].sum()

    exp = expense_df.loc[
        expense_df["month_number"] == month_number,
        "amount"
    ].sum()

    monthly_income.append(float(inc))
    monthly_expense.append(float(exp))
    monthly_balance.append(
        float(inc - exp)
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
    balance
]


# ============================================================
# YEAR SUMMARY
# ============================================================

st.subheader("🏦 Year Summary")

st.dataframe(
    summary,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# TEMPLATE PATH
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
# ALSO CHECK COMMON STREAMLIT PATHS
# ============================================================

possible_paths = [

    TEMPLATE_PATH,

    Path.cwd() /
    TEMPLATE_NAME,

    Path("/mount/src") /
    TEMPLATE_NAME,

    Path("/mount/src/value-pending") /
    TEMPLATE_NAME,

]


template_found = None

for path in possible_paths:

    if path.exists() and path.is_file():

        template_found = path

        break


# ============================================================
# DEBUG TEMPLATE LOCATION
# ============================================================

with st.expander(
    "🔧 Template path information"
):

    st.write(
        "report.py folder:",
        str(BASE_DIR)
    )

    st.write(
        "Current folder:",
        str(Path.cwd())
    )

    st.write(
        "Expected template:",
        str(TEMPLATE_PATH)
    )

    if template_found:

        st.success(
            "Template found at:"
        )

        st.code(
            str(template_found)
        )

    else:

        st.error(
            "Template NOT found."
        )


# ============================================================
# CREATE EXCEL REPORT
# ============================================================

def create_excel_report():

    if template_found is None:

        raise FileNotFoundError(
            "\n\n"
            "Excel template not found.\n\n"
            "Expected file:\n"
            f"{TEMPLATE_PATH}\n\n"
            "Make sure this file is uploaded "
            "to GitHub in the SAME folder as report.py:\n\n"
            "report.py\n"
            "MoneyMate_Annual_Budget_Template.xlsx"
        )


    # --------------------------------------------------------
    # LOAD TEMPLATE
    # --------------------------------------------------------

    wb = load_workbook(
        filename=str(template_found)
    )


    # --------------------------------------------------------
    # USE FIRST SHEET ONLY
    # --------------------------------------------------------

    ws = wb.worksheets[0]


    # --------------------------------------------------------
    # REMOVE FREEZE PANES
    # --------------------------------------------------------

    ws.freeze_panes = None


    # --------------------------------------------------------
    # REMOVE OTHER SHEETS
    # --------------------------------------------------------

    for sheet in wb.worksheets[1:]:

        wb.remove(sheet)


    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    # Keep template title formatting.

    # Update year if the template has a year cell.

    for row in ws.iter_rows():

        for cell in row:

            if isinstance(
                cell.value,
                str
            ):

                if (
                    "2024" in cell.value
                    or "2025" in cell.value
                    or "2026" in cell.value
                ):

                    cell.value = (
                        cell.value
                        .replace(
                            "2024",
                            str(selected_year)
                        )
                        .replace(
                            "2025",
                            str(selected_year)
                        )
                        .replace(
                            "2026",
                            str(selected_year)
                        )
                    )


    # --------------------------------------------------------
    # FIND TABLE HEADERS
    # --------------------------------------------------------

    def find_row_with_text(
        text
    ):

        text = str(text).strip().lower()

        for row in ws.iter_rows():

            for cell in row:

                if cell.value is None:
                    continue

                value = str(
                    cell.value
                ).strip().lower()

                if value == text:

                    return cell.row

        return None


    income_row = find_row_with_text(
        "Income"
    )

    expense_row = find_row_with_text(
        "Expenses"
    )

    if expense_row is None:

        expense_row = find_row_with_text(
            "Expense"
        )


    # --------------------------------------------------------
    # FIND MONTH HEADER
    # --------------------------------------------------------

    month_header_row = None

    for row in ws.iter_rows():

        values = [
            str(cell.value).strip()
            if cell.value is not None
            else ""
            for cell in row
        ]

        found_months = sum(
            month in values
            for month in months
        )

        if found_months >= 6:

            month_header_row = row[0].row

            break


    # --------------------------------------------------------
    # DEFAULT TEMPLATE POSITIONS
    # --------------------------------------------------------

    if month_header_row is None:

        month_header_row = 13


    # Find columns for months.

    month_columns = {}

    for cell in ws[
        month_header_row
    ]:

        if cell.value is None:
            continue

        value = str(
            cell.value
        ).strip()

        if value in months:

            month_columns[
                value
            ] = cell.column


    # --------------------------------------------------------
    # IF MONTH COLUMNS NOT FOUND,
    # USE B:M
    # --------------------------------------------------------

    if len(month_columns) < 12:

        month_columns = {}

        for index, month in enumerate(
            months,
            start=2
        ):

            month_columns[
                month
            ] = index


    # --------------------------------------------------------
    # FIND ITEM COLUMN
    # --------------------------------------------------------

    item_column = 1


    # --------------------------------------------------------
    # WRITE CATEGORY DATA
    # --------------------------------------------------------

    def write_category_data(
        table,
        start_row
    ):

        if table.empty:

            return start_row

        current_row = start_row

        for _, data_row in table.iterrows():

            ws.cell(
                current_row,
                item_column
            ).value = str(
                data_row["Item"]
            )

            for month in months:

                col = month_columns[
                    month
                ]

                ws.cell(
                    current_row,
                    col
                ).value = float(
                    data_row[month]
                )

            current_row += 1

        # Total row

        ws.cell(
            current_row,
            item_column
        ).value = "Total"

        for month in months:

            col = month_columns[
                month
            ]

            ws.cell(
                current_row,
                col
            ).value = float(
                table[month].sum()
            )

        return current_row


    # --------------------------------------------------------
    # DETERMINE START ROWS
    # --------------------------------------------------------

    income_start = (
        income_row + 2
        if income_row
        else month_header_row + 1
    )

    if expense_row:

        expense_start = (
            expense_row + 2
        )

    else:

        expense_start = (
            income_start +
            len(income_table) +
            5
        )


    # --------------------------------------------------------
    # WRITE INCOME
    # --------------------------------------------------------

    write_category_data(
        income_table,
        income_start
    )


    # --------------------------------------------------------
    # WRITE EXPENSE
    # --------------------------------------------------------

    write_category_data(
        expense_table,
        expense_start
    )


    # --------------------------------------------------------
    # SUMMARY VALUES
    # --------------------------------------------------------

    # Search labels in template and place values
    # next to them.

    summary_values = {

        "total monthly income":
            total_income,

        "total income":
            total_income,

        "total monthly expenses":
            total_expense,

        "total expenses":
            total_expense,

        "balance":
            balance,

        "percentage of income spent":
            spend_percent,

    }


    for row in ws.iter_rows():

        for cell in row:

            if cell.value is None:
                continue

            label = str(
                cell.value
            ).strip().lower()

            if label in summary_values:

                value = summary_values[
                    label
                ]

                target = ws.cell(
                    cell.row,
                    cell.column + 1
                )

                target.value = value

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


    # ========================================================
    # CHART DATA
    # ========================================================

    # Put chart source data far to the right.
    # This does not affect the visible report.

    chart_start_col = 30
    chart_start_row = 2


    # Headers

    ws.cell(
        chart_start_row,
        chart_start_col
    ).value = "Month"

    ws.cell(
        chart_start_row,
        chart_start_col + 1
    ).value = "Income"

    ws.cell(
        chart_start_row,
        chart_start_col + 2
    ).value = "Expense"


    for i, month in enumerate(
        months,
        start=1
    ):

        row = (
            chart_start_row +
            i
        )

        ws.cell(
            row,
            chart_start_col
        ).value = month

        ws.cell(
            row,
            chart_start_col + 1
        ).value = monthly_income[
            i - 1
        ]

        ws.cell(
            row,
            chart_start_col + 2
        ).value = monthly_expense[
            i - 1
        ]


    # ========================================================
    # CREATE / UPDATE BAR CHART
    # ========================================================

    # Remove existing charts.
    # Then create a reliable Excel chart.

    ws._charts = []


    bar_chart = BarChart()

    bar_chart.type = "col"

    bar_chart.style = 10

    bar_chart.title = (
        f"Monthly Income vs Expense - "
        f"{selected_year}"
    )

    bar_chart.y_axis.title = "Amount"

    bar_chart.x_axis.title = "Month"

    bar_chart.height = 8

    bar_chart.width = 16


    data_ref = Reference(
        ws,
        min_col=chart_start_col + 1,
        max_col=chart_start_col + 2,
        min_row=chart_start_row,
        max_row=chart_start_row + 12
    )


    categories_ref = Reference(
        ws,
        min_col=chart_start_col,
        min_row=chart_start_row + 1,
        max_row=chart_start_row + 12
    )


    bar_chart.add_data(
        data_ref,
        titles_from_data=True
    )

    bar_chart.set_categories(
        categories_ref
    )

    bar_chart.legend.position = "b"


    # Put chart below report.

    chart_row = max(
        expense_start +
        len(expense_table) +
        6,
        35
    )


    ws.add_chart(
        bar_chart,
        f"A{chart_row}"
    )


    # ========================================================
    # HIDE CHART DATA COLUMNS
    # ========================================================

    for col in range(
        chart_start_col,
        chart_start_col + 3
    ):

        ws.column_dimensions[
            chr(64 + col)
            if col <= 26
            else get_column_name(col)
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
# HELPER
# ============================================================

def get_column_name(
    column_number
):

    result = ""

    while column_number > 0:

        column_number, remainder = divmod(
            column_number - 1,
            26
        )

        result = (
            chr(65 + remainder)
            + result
        )

    return result


# ============================================================
# DOWNLOAD
# ============================================================

st.divider()

st.subheader(
    "📤 Download Excel Report"
)


if template_found is None:

    st.error(
        "❌ Excel template is missing."
    )

    st.info(
        "Upload this file to GitHub "
        "in the SAME folder as report.py:"
    )

    st.code(
        "MoneyMate_Annual_Budget_Template.xlsx"
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
            "✅ Excel report ready."
        )

    except Exception as e:

        st.error(
            "Unable to create Excel report:"
        )

        st.exception(e)
