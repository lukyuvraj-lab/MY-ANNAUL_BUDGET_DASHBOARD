import streamlit as st
import pandas as pd
import plotly.express as px

from utils.supabase_client import supabase

import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client

SUPABASE_URL = "https://wkelsfwfdecgqibeolnk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndrZWxzZndmZGVjZ3FpYmVvbG5rIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODU3NjExOTYsImV4cCI6MjEwMTMzNzE5Nn0.aNB1owMWx2ddzqe9m1iDF9w3PLE0diBTEaMzMMHBJYY"


supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(
    page_title="MoneyMate Dashboard",
    layout="wide"
)


st.title("💰 MoneyMate Dashboard")


# Fetch transactions

response = supabase.table(
    "transactions"
).select("*").execute()


data = response.data


if data:

    df = pd.DataFrame(data)


    # KPI calculations

    income = df[
        df["type"]=="Income"
    ]["amount"].sum()


    expense = df[
        df["type"]=="Expense"
    ]["amount"].sum()


    balance = income - expense


    savings = 0

    if income > 0:
        savings = (balance/income)*100



    # Cards

    col1,col2,col3,col4 = st.columns(4)


    col1.metric(
        "💰 Income",
        f"₹ {income:,.0f}"
    )


    col2.metric(
        "💸 Expense",
        f"₹ {expense:,.0f}"
    )


    col3.metric(
        "🏦 Balance",
        f"₹ {balance:,.0f}"
    )


    col4.metric(
        "📊 Savings %",
        f"{savings:.1f}%"
    )



    st.divider()


    # Monthly chart

    df["date"] = pd.to_datetime(df["date"])

    monthly = (
        df.groupby(
            [
                df["date"].dt.month,
                "type"
            ]
        )["amount"]
        .sum()
        .reset_index()
    )


    fig = px.bar(
        monthly,
        x="date",
        y="amount",
        color="type",
        title="📈 Monthly Income vs Expense"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )



    # Category chart

    expense_df = df[
        df["type"]=="Expense"
    ]


    if not expense_df.empty:

        category = (
            expense_df
            .groupby("category")
            ["amount"]
            .sum()
            .reset_index()
        )


        pie = px.pie(
            category,
            names="category",
            values="amount",
            title="🥧 Expense By Category"
        )


        st.plotly_chart(
            pie,
            use_container_width=True
        )



    st.divider()


    st.subheader(
        "📋 Recent Transactions"
    )


    st.dataframe(
        df.sort_values(
            "date",
            ascending=False
        ).head(10),
        use_container_width=True
    )


else:

    st.info(
        "No transactions yet"
    )
