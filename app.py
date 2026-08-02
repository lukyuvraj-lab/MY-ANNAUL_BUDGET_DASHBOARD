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

try:
    options = sorted(df[col].dropna().astype(str).unique())
except Exception:
    options = list(df[col].dropna().astype(str).unique())

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
# ==========================================================
# PART 2 - Interactive Dashboard
# ==========================================================

st.divider()
st.header("📊 Dashboard Analytics")

numeric_cols = filtered_df.select_dtypes(include="number").columns.tolist()

if len(numeric_cols) < 1:
    st.warning("No numeric columns available.")
    st.stop()

# ----------------------------------------------------------
# Select Columns
# ----------------------------------------------------------

x_col = st.selectbox(
    "X Axis",
    filtered_df.columns,
    index=0
)

y_col = st.selectbox(
    "Y Axis",
    numeric_cols,
    index=0
)

# ----------------------------------------------------------
# Dashboard KPIs
# ----------------------------------------------------------

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Records",
    len(filtered_df)
)

k2.metric(
    "Total",
    f"{filtered_df[y_col].sum():,.2f}"
)

k3.metric(
    "Average",
    f"{filtered_df[y_col].mean():,.2f}"
)

k4.metric(
    "Maximum",
    f"{filtered_df[y_col].max():,.2f}"
)

st.divider()

# ----------------------------------------------------------
# Bar Chart
# ----------------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    st.subheader("Bar Chart")

    fig = px.bar(
        filtered_df,
        x=x_col,
        y=y_col,
        color=y_col,
        text_auto=True
    )

    fig.update_layout(height=450)

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ----------------------------------------------------------
# Line Chart
# ----------------------------------------------------------

with col2:

    st.subheader("Trend")

    fig = px.line(
        filtered_df,
        x=x_col,
        y=y_col,
        markers=True
    )

    fig.update_layout(height=450)

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ----------------------------------------------------------
# Pie Chart
# ----------------------------------------------------------

if filtered_df[x_col].nunique() <= 20:

    st.subheader("Distribution")

    pie = px.pie(
        filtered_df,
        names=x_col,
        values=y_col,
        hole=.45
    )

    pie.update_layout(height=550)

    st.plotly_chart(
        pie,
        use_container_width=True
    )

# ----------------------------------------------------------
# Monthly Trend
# ----------------------------------------------------------

months = [
    "Jan","Feb","Mar","Apr","May","Jun",
    "Jul","Aug","Sep","Oct","Nov","Dec"
]

month_column = None

for col in filtered_df.columns:

    if filtered_df[col].astype(str).isin(months).any():
        month_column = col
        break

if month_column:

    st.subheader("Monthly Trend")

    month_df = (
        filtered_df
        .groupby(month_column)[y_col]
        .sum()
        .reindex(months)
        .fillna(0)
        .reset_index()
    )

    fig = px.area(
        month_df,
        x=month_column,
        y=y_col
    )

    fig.update_layout(height=450)

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ----------------------------------------------------------
# Top 10
# ----------------------------------------------------------

st.subheader("Top 10 Values")

top10 = filtered_df.nlargest(
    min(10, len(filtered_df)),
    y_col
)

fig = px.bar(
    top10,
    x=x_col,
    y=y_col,
    text_auto=True
)

fig.update_layout(height=450)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# Heatmap
# ----------------------------------------------------------

st.subheader("Correlation")

if len(numeric_cols) > 1:

    corr = filtered_df[numeric_cols].corr()

    heat = px.imshow(
        corr,
        text_auto=".2f",
        aspect="auto"
    )

    heat.update_layout(height=500)

    st.plotly_chart(
        heat,
        use_container_width=True
    )

# ----------------------------------------------------------
# Download Filtered Data
# ----------------------------------------------------------

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇ Download Filtered Data",
    csv,
    "Filtered_Budget.csv",
    "text/csv"
)
# ==========================================================
# PART 3 - Executive Features
# ==========================================================

import io

st.divider()
st.header("📈 Executive Summary")

# ----------------------------------------------------------
# Budget Health
# ----------------------------------------------------------

total = filtered_df[y_col].sum()
average = filtered_df[y_col].mean()

left, right = st.columns([3,1])

with left:

    progress = 0

    if maximum_value > 0:
        progress = min(total / maximum_value, 1.0)

    st.progress(progress)

with right:

    if progress < 0.50:
        st.success("✅ Budget Healthy")

    elif progress < 0.80:
        st.warning("⚠ Budget Watch")

    else:
        st.error("🚨 Budget Limit Reached")

# ----------------------------------------------------------
# Top Records
# ----------------------------------------------------------

st.subheader("🏆 Top Transactions")

st.dataframe(
    filtered_df.nlargest(
        min(15, len(filtered_df)),
        y_col
    ),
    use_container_width=True
)

# ----------------------------------------------------------
# Bottom Records
# ----------------------------------------------------------

st.subheader("📉 Lowest Transactions")

st.dataframe(
    filtered_df.nsmallest(
        min(15, len(filtered_df)),
        y_col
    ),
    use_container_width=True
)

# ----------------------------------------------------------
# Export to Excel
# ----------------------------------------------------------

output = io.BytesIO()

with pd.ExcelWriter(output, engine="openpyxl") as writer:

    filtered_df.to_excel(
        writer,
        sheet_name="Filtered Data",
        index=False
    )

    stats = pd.DataFrame({
        "Metric":[
            "Rows",
            "Total",
            "Average",
            "Maximum",
            "Minimum"
        ],
        "Value":[
            len(filtered_df),
            filtered_df[y_col].sum(),
            filtered_df[y_col].mean(),
            filtered_df[y_col].max(),
            filtered_df[y_col].min()
        ]
    })

    stats.to_excel(
        writer,
        sheet_name="Summary",
        index=False
    )

st.download_button(
    "📥 Download Excel Report",
    output.getvalue(),
    file_name="Budget_Report.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# ----------------------------------------------------------
# Metrics Table
# ----------------------------------------------------------

st.subheader("📋 Dashboard Metrics")

metrics = pd.DataFrame({
    "Metric":[
        "Records",
        "Total",
        "Average",
        "Maximum",
        "Minimum",
        "Unique Values"
    ],
    "Value":[
        len(filtered_df),
        round(filtered_df[y_col].sum(),2),
        round(filtered_df[y_col].mean(),2),
        round(filtered_df[y_col].max(),2),
        round(filtered_df[y_col].min(),2),
        filtered_df[x_col].nunique()
    ]
})

st.dataframe(
    metrics,
    use_container_width=True
)

# ----------------------------------------------------------
# Footer
# ----------------------------------------------------------

st.divider()

st.caption(
    "Annual Budget Dashboard | Built with Streamlit • Plotly • Pandas"
)
