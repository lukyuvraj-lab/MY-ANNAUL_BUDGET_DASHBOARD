import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Annual Budget Dashboard",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Annual Budget Dashboard")
st.caption("Professional Budget Analytics Dashboard")

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.header("Upload Budget Workbook")

uploaded_file = st.sidebar.file_uploader(
    "Select Annual Budget Excel File",
    type=["xlsx"]
)

if uploaded_file is None:
    st.info("👈 Upload your Annual Budget workbook to begin.")
    st.stop()

# -----------------------------
# Read Workbook
# -----------------------------
try:
    xl = pd.ExcelFile(uploaded_file)

    sheets = {}

    for sheet in xl.sheet_names:
        try:
            sheets[sheet] = pd.read_excel(uploaded_file, sheet_name=sheet)
        except Exception:
            pass

except Exception as e:
    st.error(e)
    st.stop()

st.success("Workbook loaded successfully.")

# -----------------------------
# Sheet Selection
# -----------------------------
sheet_name = st.sidebar.selectbox(
    "Choose Sheet",
    list(sheets.keys())
)

df = sheets[sheet_name]

# -----------------------------
# Preview
# -----------------------------
with st.expander("Preview Data"):
    st.dataframe(df, use_container_width=True)

# -----------------------------
# Numeric Columns
# -----------------------------
numeric_cols = df.select_dtypes(include="number").columns.tolist()

if len(numeric_cols) == 0:
    st.warning("No numeric columns found in this sheet.")
    st.stop()

# -----------------------------
# KPIs
# -----------------------------
total_value = df[numeric_cols].sum().sum()

average_value = df[numeric_cols].mean().mean()

maximum_value = df[numeric_cols].max().max()

minimum_value = df[numeric_cols].min().min()

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Total",
    f"{total_value:,.2f}"
)

c2.metric(
    "Average",
    f"{average_value:,.2f}"
)

c3.metric(
    "Maximum",
    f"{maximum_value:,.2f}"
)

c4.metric(
    "Minimum",
    f"{minimum_value:,.2f}"
)

st.divider()

# -----------------------------
# Filters
# -----------------------------
st.sidebar.header("Filters")

filtered_df = df.copy()

for col in df.columns:

    if df[col].dtype == object and df[col].nunique() <= 30:

        values = st.sidebar.multiselect(
            col,
            sorted(df[col].dropna().unique()),
            default=sorted(df[col].dropna().unique())
        )

        filtered_df = filtered_df[
            filtered_df[col].isin(values)
        ]

st.subheader("Filtered Data")

st.dataframe(
    filtered_df,
    use_container_width=True
)

# -----------------------------
# Summary
# -----------------------------
st.subheader("Summary Statistics")

st.dataframe(
    filtered_df.describe(include="all"),
    use_container_width=True
)

# -----------------------------
# Ready for Charts
# -----------------------------
st.info(
    "Part 2 will add interactive charts, monthly trends, "
    "expense analysis, category breakdown, savings dashboard, "
    "and budget vs actual visualizations."
)
