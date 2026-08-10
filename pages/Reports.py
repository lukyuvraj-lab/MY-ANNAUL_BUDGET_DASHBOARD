import streamlit as st
import pandas as pd
from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.chart import BarChart, Reference, PieChart
from openpyxl.chart.label import DataLabelList
from openpyxl.utils import get_column_letter

st.set_page_config(page_title='MoneyMate - Reports', page_icon='📊', layout='wide')
st.title('📊 MoneyMate - Yearly Report')

# ---------------- LOAD DATA ----------------
try:
    from utils.supabase_client import supabase
    response = supabase.table('transactions').select('*').execute()
    data = response.data
except Exception as e:
    st.error(f'Unable to load transactions: {e}')
    data = []

if not data:
    st.info('No transactions found.')
    st.stop()

df = pd.DataFrame(data)
required = ['date', 'amount', 'type', 'category']
missing = [c for c in required if c not in df.columns]
if missing:
    st.error('Missing columns in transactions table: ' + ', '.join(missing))
    st.stop()

df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
df['type'] = df['type'].fillna('').astype(str).str.strip().str.lower()
df['category'] = df['category'].fillna('Other').astype(str).str.strip()
df.loc[df['category'] == '', 'category'] = 'Other'
df = df.dropna(subset=['date'])
if df.empty:
    st.info('No valid transactions found.')
    st.stop()

months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
years = sorted(df['date'].dt.year.unique(), reverse=True)
selected_year = st.selectbox('📅 Select Year', years)
year_df = df[df['date'].dt.year == selected_year].copy()
year_df['Month'] = year_df['date'].dt.month

income_df = year_df[year_df['type'] == 'income'].copy()
expense_df = year_df[year_df['type'] == 'expense'].copy()
total_income = float(income_df['amount'].sum())
total_expense = float(expense_df['amount'].sum())
balance = total_income - total_expense
spend_pct = (total_expense / total_income * 100) if total_income else 0

# ---------------- STREAMLIT VIEW ----------------
st.subheader(f'📅 {selected_year} Overview')
c1,c2,c3,c4 = st.columns(4)
c1.metric('💰 Total Income', f'₹{total_income:,.2f}')
c2.metric('💸 Total Expense', f'₹{total_expense:,.2f}')
c3.metric('🏦 Balance', f'₹{balance:,.2f}')
c4.metric('📊 Spend %', f'{spend_pct:.2f}%')
st.divider()

def make_table(src):
    if src.empty:
        return pd.DataFrame(columns=['Item'] + months)
    t = pd.pivot_table(src, index='category', columns='Month', values='amount', aggfunc='sum', fill_value=0)
    t = t.reindex(columns=range(1,13), fill_value=0)
    t.columns = months
    t = t.reset_index().rename(columns={'category':'Item'})
    return t

income_table = make_table(income_df)
expense_table = make_table(expense_df)

st.subheader('💰 Income')
st.dataframe(income_table, use_container_width=True, hide_index=True)
st.subheader('💸 Expense')
st.dataframe(expense_table, use_container_width=True, hide_index=True)

monthly_income = income_df.groupby('Month')['amount'].sum() if not income_df.empty else pd.Series(dtype=float)
monthly_expense = expense_df.groupby('Month')['amount'].sum() if not expense_df.empty else pd.Series(dtype=float)
summary = pd.DataFrame(index=['Income','Expense','Balance'], columns=months, dtype=float)
for n,m in enumerate(months,1):
    inc = float(monthly_income.get(n,0)); exp = float(monthly_expense.get(n,0))
    summary.loc['Income',m] = inc
    summary.loc['Expense',m] = exp
    summary.loc['Balance',m] = inc-exp
summary['Year Total'] = summary.sum(axis=1)
summary_export = summary.reset_index().rename(columns={'index':'Type'})

st.subheader('🏦 Year Summary')
st.dataframe(summary_export, use_container_width=True, hide_index=True)
st.subheader('📊 Charts')
chart_df = pd.DataFrame({'Income':[monthly_income.get(i,0) for i in range(1,13)], 'Expense':[monthly_expense.get(i,0) for i in range(1,13)]}, index=months)
st.bar_chart(chart_df)

if not expense_df.empty:
    category_expense = expense_df.groupby('category', as_index=False)['amount'].sum().sort_values('amount', ascending=False)
    st.bar_chart(category_expense.set_index('category'))
else:
    category_expense = pd.DataFrame(columns=['category','amount'])

# ---------------- EXCEL REPORT ----------------
def create_excel_report():
    wb = Workbook()
    ws = wb.active
    ws.title = 'Annual Budget'
    ws.sheet_view.showGridLines = False

    # Template-like colours
    BLUE = '4F64A5'
    LIGHT_BLUE = 'D9E0F2'
    GREY = 'F2F2F2'
    WHITE = 'FFFFFF'
    BLACK = '000000'
    thin = Side(style='thin', color='D0D5DD')
    medium = Side(style='medium', color=BLUE)
    thin_border = Border(left=thin, right=thin, top=thin, bottom=thin)
    total_border = Border(top=medium, bottom=medium)
    blue_fill = PatternFill('solid', fgColor=LIGHT_BLUE)
    grey_fill = PatternFill('solid', fgColor=GREY)

    ws.column_dimensions['A'].width = 28
    for c in range(2,14): ws.column_dimensions[get_column_letter(c)].width = 11
    ws.sheet_view.zoomScale = 90
    ws.freeze_panes = 'B13'

    # Title
    ws.merge_cells('A2:M2')
    ws['A2'] = 'ANNUAL BUDGET'
    ws['A2'].font = Font(name='Arial', size=22, bold=True, color=BLACK)
    ws['A2'].alignment = Alignment(horizontal='left', vertical='center')
    ws.row_dimensions[2].height = 34
    for c in range(1,14): ws.cell(3,c).fill = PatternFill('solid', fgColor=BLUE)
    ws.row_dimensions[3].height = 5

    # Summary block
    ws.merge_cells('A4:D4'); ws['A4'] = 'SUMMARY'
    ws['A4'].font = Font(name='Arial', size=11, bold=True); ws['A4'].fill = blue_fill
    summary_rows = [(5,'Total monthly income',total_income),(6,'Total monthly expenses',total_expense),(8,'BALANCE',balance),(10,'PERCENTAGE OF INCOME SPENT',spend_pct)]
    for r,label,value in summary_rows:
        ws.cell(r,1,label); ws.cell(r,2,value)
        for c in (1,2):
            ws.cell(r,c).border = thin_border
            ws.cell(r,c).font = Font(name='Arial', size=10, bold=r in (8,10))
            if r in (8,10): ws.cell(r,c).fill = blue_fill
        ws.cell(r,2).alignment = Alignment(horizontal='right')
    for r in (5,6,8): ws.cell(r,2).number_format = '#,##0.00'
    ws['B10'].number_format = '0.00%'
    ws['B10'] = spend_pct / 100

    # Common table writer
    def write_table(title_row, header_row, start_row, table, total_label):
        ws.cell(title_row,1,'INCOME' if total_label=='Total Income' else 'EXPENSES').font = Font(name='Arial', size=16, bold=True)
        headers = ['Item'] + months
        for c,h in enumerate(headers,1):
            cell=ws.cell(header_row,c,h); cell.font=Font(name='Arial',size=10,bold=True); cell.fill=blue_fill; cell.border=thin_border; cell.alignment=Alignment(horizontal='center')
        categories = table['Item'].tolist() if not table.empty else []
        for i,cat in enumerate(categories):
            r=start_row+i
            ws.cell(r,1,cat)
            row_data=table.iloc[i]
            for c,m in enumerate(months,2): ws.cell(r,c,float(row_data[m]))
            for c in range(1,14):
                cell=ws.cell(r,c); cell.border=thin_border; cell.font=Font(name='Arial',size=9)
                if i%2: cell.fill=grey_fill
                if c>1: cell.number_format='#,##0.00'; cell.alignment=Alignment(horizontal='right')
        total_row=start_row+len(categories)
        ws.cell(total_row,1,'Total')
        for c in range(2,14):
            col=get_column_letter(c)
            ws.cell(total_row,c, f'=SUM({col}{start_row}:{col}{total_row-1})' if categories else 0)
            ws.cell(total_row,c).number_format='#,##0.00'
        for c in range(1,14):
            cell=ws.cell(total_row,c); cell.font=Font(name='Arial',size=10,bold=True); cell.fill=blue_fill; cell.border=total_border
        return total_row

    income_total_row = write_table(12,13,14,income_table,'Total Income')
    expense_title = income_total_row + 3
    expense_header = expense_title + 1
    expense_total_row = write_table(expense_title,expense_header,expense_header+1,expense_table,'Total Expense')

    # Balance
    balance_row = expense_total_row + 2
    ws.cell(balance_row,1,'BALANCE')
    for c in range(2,14):
        col=get_column_letter(c)
        ws.cell(balance_row,c,f'={col}{income_total_row}-{col}{expense_total_row}')
        ws.cell(balance_row,c).number_format='#,##0.00'
    for c in range(1,14):
        cell=ws.cell(balance_row,c); cell.font=Font(name='Arial',size=10,bold=True); cell.fill=blue_fill; cell.border=total_border

    # Hidden chart data
    data_row = balance_row + 3
    ws.cell(data_row,1,'Type')
    for c,m in enumerate(months,2): ws.cell(data_row,c,m)
    ws.cell(data_row+1,1,'INCOME'); ws.cell(data_row+2,1,'EXPENSES')
    for c in range(2,14):
        n=c-1
        ws.cell(data_row+1,c,float(monthly_income.get(n,0)))
        ws.cell(data_row+2,c,float(monthly_expense.get(n,0)))

    # Monthly chart
    chart=BarChart(); chart.type='col'; chart.style=10; chart.title='MONTHLY INCOME VS EXPENSE'; chart.y_axis.title='Amount'; chart.x_axis.title='Month'; chart.height=8; chart.width=15
    chart.add_data(Reference(ws,min_col=1,max_col=13,min_row=data_row,max_row=data_row+2),titles_from_data=True,from_rows=True)
    chart.set_categories(Reference(ws,min_col=2,max_col=13,min_row=data_row)); chart.legend.position='b'
    ws.add_chart(chart,f'A{data_row+4}')

    # Category chart
    if not category_expense.empty:
        cat_col=15
        ws.cell(data_row,cat_col,'Expense Category'); ws.cell(data_row,cat_col+1,'Amount')
        for i,row in category_expense.reset_index(drop=True).iterrows():
            ws.cell(data_row+i+1,cat_col,row['category']); ws.cell(data_row+i+1,cat_col+1,float(row['amount']))
        pie=PieChart(); pie.title='EXPENSE BY CATEGORY'; pie.height=8; pie.width=12
        pie.add_data(Reference(ws,min_col=cat_col+1,min_row=data_row,max_row=data_row+len(category_expense)),titles_from_data=True)
        pie.set_categories(Reference(ws,min_col=cat_col,min_row=data_row+1,max_row=data_row+len(category_expense)))
        pie.dataLabels=DataLabelList(); pie.dataLabels.showPercent=True
        ws.add_chart(pie,f'I{data_row+4}')

    # Hide chart data
    for r in range(data_row,data_row+100): ws.row_dimensions[r].hidden=True

    # Print/page setup like template
    ws.sheet_properties.pageSetUpPr.fitToPage=True
    ws.page_setup.fitToWidth=1; ws.page_setup.fitToHeight=0; ws.page_setup.orientation='landscape'; ws.page_setup.paperSize=ws.PAPERSIZE_A4
    ws.print_area=f'A1:M{balance_row}'

    output=BytesIO(); wb.save(output); output.seek(0)
    return output

# ---------------- DOWNLOAD ----------------
st.subheader('📤 Excel Report')
excel_file = create_excel_report()
st.download_button(label='📥 Download Annual Budget Report', data=excel_file, file_name=f'MoneyMate_Annual_Budget_{selected_year}.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

