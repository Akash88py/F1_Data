#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import streamlit as st

# Load CSV
df = pd.read_csv("results.csv")

# Title
st.title("🏎 Formula 1 Results Dashboard")

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filters")

# Season filter
seasons = sorted(df['season'].dropna().unique())
selected_season = st.sidebar.multiselect("Select Season(s)", seasons, default=seasons)

# Driver filter
drivers = sorted((df['driver_given_name'] + " " + df['driver_family_name']).unique())
selected_drivers = st.sidebar.multiselect("Select Driver(s)", drivers)

# Constructor filter
constructors = sorted(df['constructor_name'].unique())
selected_constructors = st.sidebar.multiselect("Select Constructor(s)", constructors)

# Apply filters
filtered_df = df[df['season'].isin(selected_season)]
if selected_drivers:
    filtered_df = filtered_df[(filtered_df['driver_given_name'] + " " + filtered_df['driver_family_name']).isin(selected_drivers)]
if selected_constructors:
    filtered_df = filtered_df[filtered_df['constructor_name'].isin(selected_constructors)]

# --- Key Metrics ---
st.header("📊 Key Metrics")

total_races = filtered_df['race_name'].nunique()
total_drivers = filtered_df['driver_id'].nunique()
total_constructors = filtered_df['constructor_id'].nunique()
total_points = filtered_df['points'].sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Races", total_races)
col2.metric("Unique Drivers", total_drivers)
col3.metric("Unique Constructors", total_constructors)
col4.metric("Total Points", int(total_points))

# --- Top Performing Drivers ---
st.header("🏁 Top 10 Drivers by Points")
top_drivers = (
    filtered_df.groupby(["driver_given_name", "driver_family_name"])['points']
    .sum()
    .reset_index()
)
top_drivers['driver'] = top_drivers['driver_given_name'] + " " + top_drivers['driver_family_name']
top_drivers = top_drivers[['driver','points']].sort_values(by="points", ascending=False).head(10)
st.bar_chart(top_drivers.set_index("driver"))

# --- Top Constructors ---
st.header("🏆 Top 10 Constructors by Points")
top_constructors = (
    filtered_df.groupby("constructor_name")['points']
    .sum()
    .reset_index()
    .sort_values(by="points", ascending=False)
    .head(10)
)
st.bar_chart(top_constructors.set_index("constructor_name"))

# --- Drivers by Nationality ---
st.header("🌍 Drivers by Nationality")
drivers_by_country = (
    filtered_df.groupby("driver_nationality")['driver_id']
    .nunique()
    .reset_index()
    .sort_values(by="driver_id", ascending=False)
)
st.bar_chart(drivers_by_country.set_index("driver_nationality"))

# --- Investment Insights ---
st.header("💡 Investment Insights")

# Growth in points by constructor (year over year)
constructor_trends = (
    filtered_df.groupby(['season', 'constructor_name'])['points']
    .sum()
    .reset_index()
    .sort_values(by=['constructor_name','season'])
)

st.subheader("📈 Constructor Performance Over Time")
st.line_chart(constructor_trends.pivot(index="season", columns="constructor_name", values="points"))

# Growth in points by driver (trend of top drivers only)
st.subheader("📈 Driver Performance Trends (Top Drivers)")
top_driver_names = top_drivers['driver'].head(5).tolist()
filtered_df['driver'] = filtered_df['driver_given_name'] + " " + filtered_df['driver_family_name']
driver_trends = (
    filtered_df[filtered_df['driver'].isin(top_driver_names)]
    .groupby(['season','driver'])['points']
    .sum()
    .reset_index()
)
st.line_chart(driver_trends.pivot(index="season", columns="driver", values="points"))

# Nationality dominance
st.subheader("🌍 Nationality Points Share Over Time")
nationality_trends = (
    filtered_df.groupby(['season','driver_nationality'])['points']
    .sum()
    .reset_index()
)
st.area_chart(nationality_trends.pivot(index="season", columns="driver_nationality", values="points"))


# In[ ]:




