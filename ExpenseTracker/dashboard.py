import streamlit as st
import requests
import pandas as pd
import plotly.express as px

BASE_URL = "http://127.0.0.1:8000"

st.title("Expense Tracking & Budget Management Dashboard")

token = st.text_input(
       "Paste JWT Token",
    type="password"
)

if token:

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Dashboard Data
    dashboard = requests.get(
        f"{BASE_URL}/dashboard",
        headers=headers
    ).json()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Budget",
        dashboard["total_budget"]
    )

    col2.metric(
        "Total Expense",
        dashboard["total_expense"]
    )

    col3.metric(
        "Remaining",
        dashboard["remaining"]
    )

    st.divider()

    # Budget Report
    report = requests.get(
        f"{BASE_URL}/budget-report",
        headers=headers
    ).json()

    st.subheader("Budget Utilization")

    utilization = report["utilization_percentage"]

    st.progress(
        min(int(utilization), 100)
    )

    st.write(
        f"{utilization}% utilized"
    )

    st.divider()

    # Category Summary
    category_data = requests.get(
        f"{BASE_URL}/expenses/category-summary",
        headers=headers
    ).json()

    if len(category_data) > 0:

        df = pd.DataFrame(category_data)

        fig = px.pie(
            df,
            names="category",
            values="total",
            title="Expense Category Distribution"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.dataframe(df)