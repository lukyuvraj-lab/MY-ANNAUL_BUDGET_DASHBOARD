import streamlit as st
import pandas as pd
from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.chart import BarChart, Reference
from openpyxl.utils import get_column_letter


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

income_categories = sorted([
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
])

expense_categories = sorted([
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
])

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
# CHECK REQUIRED COLUMNS
# ============================================================

required_columns = [
    "date",
    "amount",
    "type",
    "category"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    st.error(
        "Missing columns: "
        + ", ".join(missing_columns)
    )
    st.stop()


# ============================================================
# CLEAN DATA
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
    .fillna("")
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
        "No transactions found for this year."
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

total_balance = (
    total_income -
    total_expense
)

if total_income > 0:
    spend_percent = (
        total_expense /
        total_income
    ) * 100
else:
    spend_percent = 0


# ============================================================
# KPI DISPLAY
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
# BUILD CATEGORY TABLE
# ============================================================

def build_category_table(
    source_df,
    categories
):

    table = pd.DataFrame(
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

            if category not in (
                grouped
                .index
                .get_level_values("category")
            ):
                continue

            for month_number in range(1, 13):

                try:
                    value = grouped.loc[
                        (
                            category,
                            month_number
                        )
                    ]
                except KeyError:
                    value = 0

                table.loc[
                    category,
                    months[
                        month_number - 1
                    ]
                ] = float(value)

    table.index.name = "Category"

    table["Total"] = (
        table.sum(axis=1)
    )

    return table.reset_index()


income_table = build_category_table(
    income_df,
    income_categories
)

expense_table = build_category_table(
    expense_df,
    expense_categories
)


# ============================================================
# SHOW INCOME
# ============================================================

st.subheader("💰 Income")

st.dataframe(
    income_table,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# SHOW EXPENSE
# ============================================================

st.subheader("💸 Expense")

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
            income_value -
            expense_value
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
# CHART
# ============================================================

st.subheader(
    "📊 Monthly Income vs Expense"
)

chart_df = pd.DataFrame({
    "Month": months,
    "Income": monthly_income,
    "Expense": monthly_expense
})

st.bar_chart(
    chart_df.set_index("Month"),
    use_container_width=True
)


# ============================================================
# CREATE EXCEL
# NO TEMPLATE REQUIRED
# ONE SHEET ONLY
# ============================================================

def create_excel_report():

    wb = Workbook()

    ws = wb.active

    ws.title = "Yearly Report"


    # ========================================================
    # COLORS
    # ========================================================

    title_fill = PatternFill(
        "solid",
        fgColor="1F4E78"
    )

    header_fill = PatternFill(
        "solid",
        fgColor="5B9BD5"
    )

    section_fill = PatternFill(
        "solid",
        fgColor="D9EAF7"
    )

    total_fill = PatternFill(
        "solid",
        fgColor="E2F0D9"
    )


    # ========================================================
    # FONTS
    # ========================================================

    title_font = Font(
        name="Calibri",
        size=16,
        bold=True,
        color="FFFFFF"
    )

    section_font = Font(
        name="Calibri",
        size=13,
        bold=True
    )

    header_font = Font(
        name="Calibri",
        size=11,
        bold=True,
        color="FFFFFF"
    )

    normal_font = Font(
        name="Calibri",
        size=11
    )

    bold_font = Font(
        name="Calibri",
        size=11,
        bold=True
    )


    # ========================================================
    # BORDER
    # ========================================================

    thin_side = Side(
        style="thin",
        color="B7B7B7"
    )

    border = Border(
        left=thin_side,
        right=thin_side,
        top=thin_side,
        bottom=thin_side
    )


    # ========================================================
    # TITLE
    # ========================================================

    ws.merge_cells(
        start_row=1,
        start_column=1,
        end_row=1,
        end_column=14
    )

    title_cell = ws.cell(
        1,
        1
    )

    title_cell.value = (
        f"MoneyMate - Annual Report "
        f"{selected_year}"
    )

    title_cell.fill = title_fill

    title_cell.font = title_font

    title_cell.alignment = Alignment(
        horizontal="center",
        vertical="center"
    )

    ws.row_dimensions[1].height = 30


    # ========================================================
    # KPI
    # ========================================================

    kpis = [
        (
            "Total Income",
            total_income
        ),
        (
            "Total Expense",
            total_expense
        ),
        (
            "Balance",
            total_balance
        ),
        (
            "Spend %",
            spend_percent
        )
    ]


    for col, (label, value) in enumerate(
        kpis,
        start=1
    ):

        label_cell = ws.cell(
            3,
            col
        )

        label_cell.value = label

        label_cell.fill = section_fill

        label_cell.font = bold_font

        label_cell.border = border

        label_cell.alignment = Alignment(
            horizontal="center"
        )


        value_cell = ws.cell(
            4,
            col
        )

        value_cell.value = value

        value_cell.font = bold_font

        value_cell.border = border

        value_cell.alignment = Alignment(
            horizontal="center"
        )

        if label == "Spend %":

            value_cell.number_format = (
                '0.00"%"'
            )

        else:

            value_cell.number_format = (
                '#,##0.00'
            )


    # ========================================================
    # COMMON HEADERS
    # ========================================================

    table_headers = [
        "Category"
    ] + months + [
        "Total"
    ]


    # ========================================================
    # INCOME SECTION
    # ========================================================

    income_section_row = 7

    ws.merge_cells(
        start_row=income_section_row,
        start_column=1,
        end_row=income_section_row,
        end_column=14
    )

    cell = ws.cell(
        income_section_row,
        1
    )

    cell.value = "INCOME"

    cell.fill = section_fill

    cell.font = section_font


    income_header_row = (
        income_section_row + 1
    )


    for col, header in enumerate(
        table_headers,
        start=1
    ):

        cell = ws.cell(
            income_header_row,
            col
        )

        cell.value = header

        cell.fill = header_fill

        cell.font = header_font

        cell.border = border

        cell.alignment = Alignment(
            horizontal="center"
        )


    for row_index, row in income_table.iterrows():

        excel_row = (
            income_header_row +
            1 +
            row_index
        )

        for col_index, column in enumerate(
            table_headers,
            start=1
        ):

            cell = ws.cell(
                excel_row,
                col_index
            )

            cell.value = row[column]

            cell.font = normal_font

            cell.border = border

            if col_index > 1:

                cell.number_format = (
                    '#,##0.00'
                )


    income_total_row = (
        income_header_row +
        1 +
        len(income_table)
    )


    ws.cell(
        income_total_row,
        1
    ).value = "Total Income"


    for col in range(2, 15):

        column_letter = get_column_letter(
            col
        )

        cell = ws.cell(
            income_total_row,
            col
        )

        cell.value = (
            f"=SUM("
            f"{column_letter}"
            f"{income_header_row + 1}:"
            f"{column_letter}"
            f"{income_total_row - 1}"
            f")"
        )

        cell.number_format = (
            '#,##0.00'
        )


    for col in range(1, 15):

        cell = ws.cell(
            income_total_row,
            col
        )

        cell.fill = total_fill

        cell.font = bold_font

        cell.border = border


    # ========================================================
    # EXPENSE SECTION
    # ========================================================

    expense_section_row = (
        income_total_row + 3
    )

    ws.merge_cells(
        start_row=expense_section_row,
        start_column=1,
        end_row=expense_section_row,
        end_column=14
    )

    cell = ws.cell(
        expense_section_row,
        1
    )

    cell.value = "EXPENSE"

    cell.fill = section_fill

    cell.font = section_font


    expense_header_row = (
        expense_section_row + 1
    )


    for col, header in enumerate(
        table_headers,
        start=1
    ):

        cell = ws.cell(
            expense_header_row,
            col
        )

        cell.value = header

        cell.fill = header_fill

        cell.font = header_font

        cell.border = border

        cell.alignment = Alignment(
            horizontal="center"
        )


    for row_index, row in expense_table.iterrows():

        excel_row = (
            expense_header_row +
            1 +
            row_index
        )

        for col_index, column in enumerate(
            table_headers,
            start=1
        ):

            cell = ws.cell(
                excel_row,
                col_index
            )

            cell.value = row[column]

            cell.font = normal_font

            cell.border = border

            if col_index > 1:

                cell.number_format = (
                    '#,##0.00'
                )


    expense_total_row = (
        expense_header_row +
        1 +
        len(expense_table)
    )


    ws.cell(
        expense_total_row,
        1
    ).value = "Total Expense"


    for col in range(2, 15):

        column_letter = get_column_letter(
            col
        )

        cell = ws.cell(
            expense_total_row,
            col
        )

        cell.value = (
            f"=SUM("
            f"{column_letter}"
            f"{expense_header_row + 1}:"
            f"{column_letter}"
            f"{expense_total_row - 1}"
            f")"
        )

        cell.number_format = (
            '#,##0.00'
        )


    for col in range(1, 15):

        cell = ws.cell(
            expense_total_row,
            col
        )

        cell.fill = total_fill

        cell.font = bold_font

        cell.border = border


    # ========================================================
    # YEAR SUMMARY SECTION
    # ========================================================

    summary_section_row = (
        expense_total_row + 3
    )

    ws.merge_cells(
        start_row=summary_section_row,
        start_column=1,
        end_row=summary_section_row,
        end_column=14
    )

    cell = ws.cell(
        summary_section_row,
        1
    )

    cell.value = "YEAR SUMMARY"

    cell.fill = section_fill

    cell.font = section_font


    summary_header_row = (
        summary_section_row + 1
    )

    summary_headers = [
        "Type"
    ] + months + [
        "Year Total"
    ]


    for col, header in enumerate(
        summary_headers,
        start=1
    ):

        cell = ws.cell(
            summary_header_row,
            col
        )

        cell.value = header

        cell.fill = header_fill

        cell.font = header_font

        cell.border = border

        cell.alignment = Alignment(
            horizontal="center"
        )


    for row_index, row in summary.iterrows():

        excel_row = (
            summary_header_row +
            1 +
            row_index
        )

        for col_index, column in enumerate(
            summary_headers,
            start=1
        ):

            cell = ws.cell(
                excel_row,
                col_index
            )

            cell.value = row[column]

            cell.font = normal_font

            cell.border = border

            if col_index > 1:

                cell.number_format = (
                    '#,##0.00'
                )


    # ========================================================
    # CHART DATA
    # ========================================================

    chart_column = 17

    chart_header_row = 2


    ws.cell(
        chart_header_row,
        chart_column
    ).value = "Month"

    ws.cell(
        chart_header_row,
        chart_column + 1
    ).value = "Income"

    ws.cell(
        chart_header_row,
        chart_column + 2
    ).value = "Expense"


    for i, month in enumerate(
        months,
        start=1
    ):

        row = (
            chart_header_row + i
        )

        ws.cell(
            row,
            chart_column
        ).value = month

        ws.cell(
            row,
            chart_column + 1
        ).value = monthly_income[
            i - 1
        ]

        ws.cell(
            row,
            chart_column + 2
        ).value = monthly_expense[
            i - 1
        ]


    # ========================================================
    # BAR CHART
    # ========================================================

    chart = BarChart()

    chart.type = "col"

    chart.style = 10

    chart.title = (
        f"Monthly Income vs Expense "
        f"- {selected_year}"
    )

    chart.y_axis.title = "Amount"

    chart.x_axis.title = "Month"

    chart.height = 8

    chart.width = 16


    data_reference = Reference(
        ws,
        min_col=chart_column + 1,
        max_col=chart_column + 2,
        min_row=chart_header_row,
        max_row=chart_header_row + 12
    )


    category_reference = Reference(
        ws,
        min_col=chart_column,
        min_row=chart_header_row + 1,
        max_row=chart_header_row + 12
    )


    chart.add_data(
        data_reference,
        titles_from_data=True
    )

    chart.set_categories(
        category_reference
    )

    chart.legend.position = "b"


    chart_location_row = (
        summary_header_row + 6
    )


    ws.add_chart(
        chart,
        f"A{chart_location_row}"
    )


    # ========================================================
    # HIDE CHART DATA
    # ========================================================

    for col in range(
        chart_column,
        chart_column + 3
    ):

        ws.column_dimensions[
            get_column_letter(col)
        ].hidden = True


    # ========================================================
    # COLUMN WIDTHS
    # ========================================================

    ws.column_dimensions["A"].width = 30

    for col in range(2, 15):

        ws.column_dimensions[
            get_column_letter(col)
        ].width = 13


    # ========================================================
    # EXCEL SETTINGS
    # ========================================================

    # IMPORTANT:
    # No freeze panes.

    ws.freeze_panes = None

    ws.sheet_view.showGridLines = False


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

st.subheader("📤 Excel Export")


try:

    excel_file = create_excel_report()

    st.download_button(
        label="📥 Download Yearly Report Excel",
        data=excel_file,
        file_name=(
            f"MoneyMate_Yearly_Report_"
            f"{selected_year}.xlsx"
        ),
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        use_container_width=True
    )

except Exception as e:

    st.error(
        f"Unable to create Excel report: {e}"
    )
