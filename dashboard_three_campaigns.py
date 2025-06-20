
import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="3-Campaign Comparison Dashboard", layout="wide")

@st.cache_data
def load_data():
    df1 = pd.read_excel("Template _ Campaigns Comparison.xlsx", sheet_name="Campaign 1")
    df2 = pd.read_excel("Template _ Campaigns Comparison.xlsx", sheet_name="Campaign 2")
    df3 = pd.read_excel("Template _ Campaigns Comparison.xlsx", sheet_name="Campaign 3")

    df1 = df1.rename(columns={df1.columns[0]: "Metric"})
    df2 = df2.rename(columns={df2.columns[0]: "Metric"})
    df3 = df3.rename(columns={df3.columns[0]: "Metric"})

    df1 = df1.melt(id_vars="Metric", var_name="Week", value_name="Value")
    df1["Campaign"] = "Campaign 1"
    df2 = df2.melt(id_vars="Metric", var_name="Week", value_name="Value")
    df2["Campaign"] = "Campaign 2"
    df3 = df3.melt(id_vars="Metric", var_name="Week", value_name="Value")
    df3["Campaign"] = "Campaign 3"

    return pd.concat([df1, df2, df3], ignore_index=True)

df_all = load_data()

st.markdown("## 🎯 3-Campaign Performance Dashboard")

compare_mode = st.checkbox("Compare Mode", value=False)

if compare_mode:
    available_metrics = df_all["Metric"].unique().tolist()
    metric = st.selectbox("Select a metric to compare", available_metrics)
    campaigns = st.multiselect("Select campaigns to compare", options=df_all["Campaign"].unique(), default=df_all["Campaign"].unique())

    filtered = df_all[(df_all["Metric"] == metric) & (df_all["Campaign"].isin(campaigns))].copy()
    filtered["Value"] = pd.to_numeric(filtered["Value"], errors="coerce")
    y_min = filtered["Value"].min() * 0.95
    y_max = filtered["Value"].max() * 1.05

    chart = alt.Chart(filtered).mark_line(point=True).encode(
        x=alt.X("Week:N", title="Week"),
        y=alt.Y("Value:Q", title="Value", scale=alt.Scale(domain=[y_min, y_max])),
        color=alt.Color("Campaign:N"),
        tooltip=["Week", "Campaign", "Value"]
    ).properties(title=f"{metric} Comparison", height=400)

    st.altair_chart(chart, use_container_width=True)

else:
    st.info("Toggle Compare Mode to begin comparing campaigns.")
