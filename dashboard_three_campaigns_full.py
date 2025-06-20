
import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Campaign Comparison", layout="wide")

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

col1, col2 = st.columns([1, 8])
with col1:
    compare_mode = st.checkbox("", value=False)
with col2:
    st.markdown("<strong style='font-size:18px;'>Compare Mode</strong>", unsafe_allow_html=True)

def plot_chart(data, title, y_min=None, y_max=None, height=400, color_by="Metric"):
    chart = alt.Chart(data).mark_line(point=True).encode(
        x=alt.X("Week:N", title="Week"),
        y=alt.Y("Value:Q", title="Value", scale=alt.Scale(domain=[y_min, y_max])),
        color=alt.Color(f"{color_by}:N", title=color_by),
        tooltip=["Week", color_by, "Value"]
    ).properties(title=title, height=height)
    return chart

if compare_mode:
    selected_metric = st.selectbox("Select a metric to compare", df_all["Metric"].unique(), key="metric_compare")
    selected_campaigns = st.multiselect("Select campaigns", df_all["Campaign"].unique(), default=df_all["Campaign"].unique())

    filtered = df_all[(df_all["Metric"] == selected_metric) & (df_all["Campaign"].isin(selected_campaigns))].copy()
    filtered["Value"] = pd.to_numeric(filtered["Value"], errors="coerce")
    y_min = filtered["Value"].min() * 0.95
    y_max = filtered["Value"].max() * 1.05

    chart_type = st.radio("Chart Type", ["Line", "Bar"], horizontal=True)
    if chart_type == "Line":
        st.altair_chart(plot_chart(filtered, f"{selected_metric} Comparison", y_min, y_max, color_by="Campaign"), use_container_width=True)
    else:
        bar = alt.Chart(filtered).mark_bar().encode(
            x="Week:N",
            y=alt.Y("Value:Q", scale=alt.Scale(domain=[y_min, y_max])),
            color="Campaign:N",
            tooltip=["Week", "Campaign", "Value"]
        ).properties(title=f"{selected_metric} Comparison", height=400)
        st.altair_chart(bar, use_container_width=True)
    st.stop()

# Normal tabbed view
campaigns = df_all["Campaign"].unique()
tabs = st.tabs(list(campaigns))

for i, tab in enumerate(tabs):
    with tab:
        st.markdown(f"### {campaigns[i]}")
        df_campaign = df_all[df_all["Campaign"] == campaigns[i]]
        perf = ["Net MAU intake", "Gross MAU Intake", "Activations", "Reactivations", "Registrations"]
        plat = ["Retention D60", "Content Hours/MAU"]
        spend = ["TV Spend", "Digital Spend", "AMP Spend", "Other media spend (OOH, Metro & Buses)"]

        with st.expander("📈 Performance Metrics"):
            selected = st.multiselect(f"Select Performance Metrics ({campaigns[i]})", perf, default=perf, key=f"perf_{i}")
            if selected:
                long_df = df_campaign[df_campaign["Metric"].isin(selected)]
                st.altair_chart(plot_chart(long_df, "Performance Metrics", 0, 600000), use_container_width=True)

        with st.expander("🧩 Platform Metrics"):
            for m in plat:
                if m in df_campaign["Metric"].values:
                    df_metric = df_campaign[df_campaign["Metric"] == m]
                    ymin, ymax = (0.3, 0.6) if m == "Retention D60" else (7, 11)
                    st.altair_chart(plot_chart(df_metric, m, ymin, ymax, height=250), use_container_width=True)

        with st.expander("💰 Spend Metrics"):
            selected = st.multiselect(f"Select Spend Metrics ({campaigns[i]})", spend, default=spend, key=f"spend_{i}")
            if selected:
                long_df = df_campaign[df_campaign["Metric"].isin(selected)]
                st.altair_chart(plot_chart(long_df, "Spend Metrics", 0, 100000), use_container_width=True)
