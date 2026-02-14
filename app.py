import streamlit as st
import pandas as pd
import numpy as np
import re
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="AI Workflow Optimization Dashboard",
                   layout="wide")

st.title("🤖 AI Workflow Optimization Dashboard")
st.markdown("Operational Workflow Performance & AI-Based Insights")

# ==============================
# Load Dataset
# ==============================
@st.cache_data
def load_data():
    df = pd.read_csv("AI_Workflow_Optimization_Dataset_2500_Rows_v1.csv")
    return df

df = load_data()

# ==============================
# DATA CLEANING & TRANSFORMATION
# ==============================

# Convert dates
df["Start_Time"] = pd.to_datetime(df["Start_Time"])
df["End_Time"] = pd.to_datetime(df["End_Time"])

# Handle missing values
df.fillna({"Approval_Level": "Not Required"}, inplace=True)

# Regex extraction (Extract Employee ID number)
df["Employee_ID_Number"] = df["Assigned_Employee"].apply(
    lambda x: re.findall(r'\d+', x)[0] if re.findall(r'\d+', x) else None
)

# Create new features
df["Duration_Difference"] = df["Actual_Duration"] - df["Estimated_Duration"]
df["Delay_Flag"] = np.where(df["Duration_Difference"] > 0, "Delayed", "On-Time")

# ==============================
# SIDEBAR FILTERS
# ==============================
st.sidebar.header("🔎 Filters")

department_filter = st.sidebar.multiselect(
    "Select Department",
    options=df["Department"].unique(),
    default=df["Department"].unique()
)

priority_filter = st.sidebar.multiselect(
    "Select Priority",
    options=df["Priority_Level"].unique(),
    default=df["Priority_Level"].unique()
)

delay_filter = st.sidebar.multiselect(
    "Delay Status",
    options=df["Delay_Flag"].unique(),
    default=df["Delay_Flag"].unique()
)

filtered_df = df[
    (df["Department"].isin(department_filter)) &
    (df["Priority_Level"].isin(priority_filter)) &
    (df["Delay_Flag"].isin(delay_filter))
]

# ==============================
# KPI SECTION
# ==============================
st.subheader("📊 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Tasks", len(filtered_df))
col2.metric("Avg Actual Duration",
            round(filtered_df["Actual_Duration"].mean(), 2))
col3.metric("Total Cost",
            f"₹ {round(filtered_df['Cost_Per_Task'].sum(),2)}")
col4.metric("Delay %", 
            f"{round((filtered_df['Delay_Flag'].value_counts(normalize=True).get('Delayed',0))*100,2)} %")

# ==============================
# VISUALIZATIONS
# ==============================

st.subheader("📈 Workflow Visualizations")

col1, col2 = st.columns(2)

with col1:
    fig1 = px.bar(filtered_df,
                  x="Department",
                  y="Cost_Per_Task",
                  color="Delay_Flag",
                  title="Department-wise Cost Distribution")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.box(filtered_df,
                  x="Priority_Level",
                  y="Actual_Duration",
                  color="Priority_Level",
                  title="Duration by Priority Level")
    st.plotly_chart(fig2, use_container_width=True)

# Delay Trend Over Time
st.subheader("⏳ Delay Trend Over Time")

trend_df = filtered_df.groupby(
    filtered_df["Start_Time"].dt.date)["Delay_Flag"].value_counts().unstack().fillna(0)

fig3 = px.line(trend_df,
               title="Daily Delay Trend")
st.plotly_chart(fig3, use_container_width=True)

# ==============================
# WORKLOAD ANALYSIS
# ==============================

st.subheader("👨‍💼 Workload Distribution")

workload_df = filtered_df.groupby("Assigned_Employee")["Actual_Duration"].sum().reset_index()

fig4 = px.bar(workload_df.sort_values("Actual_Duration", ascending=False).head(10),
              x="Assigned_Employee",
              y="Actual_Duration",
              title="Top 10 Employees by Workload")
st.plotly_chart(fig4, use_container_width=True)

# ==============================
# AI RECOMMENDATION ENGINE
# ==============================

st.subheader("🧠 AI Business Insights & Recommendations")

def generate_insights(data):
    insights = []

    delay_rate = (data["Delay_Flag"] == "Delayed").mean()

    if delay_rate > 0.3:
        insights.append("⚠ High delay rate detected. Consider redistributing workload or revising time estimation models.")

    high_cost_dept = data.groupby("Department")["Cost_Per_Task"].mean().idxmax()
    insights.append(f"💰 {high_cost_dept} department shows highest average cost per task. Audit cost drivers.")

    overloaded_emp = data.groupby("Assigned_Employee")["Actual_Duration"].sum().idxmax()
    insights.append(f"👨‍💼 {overloaded_emp} appears overloaded. Workload balancing recommended.")

    high_priority_delay = data[(data["Priority_Level"] == "High") & (data["Delay_Flag"] == "Delayed")]
    if len(high_priority_delay) > 0:
        insights.append("🚨 High priority tasks are being delayed. Escalation policy review suggested.")

    return insights

recommendations = generate_insights(filtered_df)

for rec in recommendations:
    st.write(rec)

st.markdown("---")
st.markdown("### 📌 Project: AI Workflow Optimization | Built with Streamlit")
