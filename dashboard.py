#!/usr/bin/env python
# coding: utf-8

# In[3]:


import streamlit as st
import pandas as pd

# --- Load your data ---
df = pd.read_csv("results.csv")   # 👈 replace with your file path

# If season is not numeric, make sure to fix it
df['season'] = pd.to_numeric(df['season'], errors='coerce')
df = df.dropna(subset=['season'])
df['season'] = df['season'].astype(int)

# --- Comparison Mode ---
st.header("⚔️ Compare Two Investments")

compare_type = st.radio("Compare By:", ["Driver", "Constructor"], horizontal=True)

if compare_type == "Driver":
    choice1 = st.selectbox("Select First Driver", sorted((df['driver_given_name'] + " " + df['driver_family_name']).unique()), key="c1")
    choice2 = st.selectbox("Select Second Driver", sorted((df['driver_given_name'] + " " + df['driver_family_name']).unique()), key="c2")

    comp_df = (
        df.assign(driver=df['driver_given_name'] + " " + df['driver_family_name'])
        .groupby(['season','driver'])['points']
        .sum()
        .reset_index()
    )
elif compare_type == "Constructor":
    choice1 = st.selectbox("Select First Constructor", sorted(df['constructor_name'].unique()), key="c3")
    choice2 = st.selectbox("Select Second Constructor", sorted(df['constructor_name'].unique()), key="c4")

    comp_df = (
        df.groupby(['season','constructor_name'])['points']
        .sum()
        .reset_index()
        .rename(columns={'constructor_name':'driver'})
    )

# Function to compute metrics
def compute_metrics(trend):
    if len(trend) > 1:
        first_points = trend.iloc[0]['points']
        last_points = trend.iloc[-1]['points']
        years = trend['season'].nunique()
        if first_points > 0:
            cagr = ((last_points / first_points) ** (1/years) - 1) * 100
        else:
            cagr = 0
    else:
        cagr = 0

    trend['YoY_Return'] = trend['points'].pct_change() * 100
    volatility = trend['YoY_Return'].std(skipna=True)
    risk_adjusted = cagr / volatility if volatility and volatility > 0 else 0

    return cagr, volatility, risk_adjusted

# Filter data
t1 = comp_df[comp_df['driver'] == choice1]
t2 = comp_df[comp_df['driver'] == choice2]

# Display trends
st.subheader("📊 Historical Performance Trends")
st.line_chart(
    comp_df[comp_df['driver'].isin([choice1, choice2])].pivot(index="season", columns="driver", values="points")
)

# Calculate metrics
cagr1, vol1, ra1 = compute_metrics(t1)
cagr2, vol2, ra2 = compute_metrics(t2)

# Show metrics side by side
st.subheader("⚖️ Side-by-Side Metrics")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"### 🏎️ {choice1}")
    st.metric("📈 CAGR", f"{cagr1:.2f}%")
    st.metric("📊 Volatility", f"{vol1:.2f}%")
    st.metric("⚖️ Risk-Adjusted Return", f"{ra1:.2f}")

with col2:
    st.markdown(f"### 🏎️ {choice2}")
    st.metric("📈 CAGR", f"{cagr2:.2f}%")
    st.metric("📊 Volatility", f"{vol2:.2f}%")
    st.metric("⚖️ Risk-Adjusted Return", f"{ra2:.2f}")

# --- Winner Highlight ---
st.subheader("🏆 Investment Recommendation")

if ra1 > ra2:
    st.success(f"✅ **{choice1}** is the better investment choice with a higher Risk-Adjusted Return ({ra1:.2f} vs {ra2:.2f}).")
elif ra2 > ra1:
    st.success(f"✅ **{choice2}** is the better investment choice with a higher Risk-Adjusted Return ({ra2:.2f} vs {ra1:.2f}).")
else:
    st.info("⚖️ Both have similar Risk-Adjusted Returns — no clear winner.")


# In[ ]:




