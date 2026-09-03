import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt

# Page Configuration
st.set_page_config(page_title="Data Detective Agent", page_icon="🔍", layout="wide")

st.title("🔍 Project 6: Data Detective Agent")
st.markdown("Upload raw transaction data to clean missing values, compute summary metrics, and visualize category distributions.")

# --- Helper Functions ---
def clean_and_impute_data(df):
    """
    Cleans raw dataframe:
    1. Standardizes text strings.
    2. Converts Revenue to numeric, coercing bad entries.
    3. Imputes missing Revenue with median per Category (or overall median).
    4. Fills missing Category entries with 'Unknown'.
    """
    df_clean = df.copy()
    
    # 1. Clean Category strings
    if 'Category' in df_clean.columns:
        df_clean['Category'] = df_clean['Category'].astype(str).str.strip().str.title()
        df_clean['Category'] = df_clean['Category'].replace(['Nan', 'None', ''], 'Unknown')
    else:
        df_clean['Category'] = 'Uncategorized'
        
    # 2. Convert Revenue to numeric (handles strings like "$100", corrupted values)
    if 'Revenue' in df_clean.columns:
        df_clean['Revenue'] = df_clean['Revenue'].astype(str).str.replace(r'[\$,]', '', regex=True)
        df_clean['Revenue'] = pd.to_numeric(df_clean['Revenue'], errors='coerce')
        
        # 3. Impute missing values using median per category
        df_clean['Revenue'] = df_clean.groupby('Category')['Revenue'].transform(
            lambda x: x.fillna(x.median() if not np.isnan(x.median()) else 0)
        )
        # Final fallback for any remaining NaNs
        overall_median = df_clean['Revenue'].median()
        df_clean['Revenue'] = df_clean['Revenue'].fillna(overall_median if not np.isnan(overall_median) else 0.0)
    else:
        st.error("Uploaded CSV must contain a 'Revenue' column.")
        
    return df_clean

def generate_sample_csv():
    """Generates messy transaction data for demo purposes."""
    data = {
        'Transaction_ID': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
        'Category': ['Electronics', 'Clothing', 'Electronics', 'Home', None, 'Clothing', 'electronics', 'HOME', 'Clothing', 'Electronics'],
        'Revenue': ['$150.00', '45.50', 'invalid_str', None, '200.0', '55.00', '120', None, '49.99', '$310.00']
    }
    return pd.DataFrame(data)

# --- Sidebar File Handling ---
st.sidebar.header("📁 Data Source")
uploaded_file = st.sidebar.file_uploader("Upload Raw CSV", type=["csv"])

if st.sidebar.button("Load Sample Messy Dataset"):
    raw_df = generate_sample_csv()
elif uploaded_file is not None:
    raw_df = pd.read_csv(uploaded_file)
else:
    raw_df = generate_sample_csv() # Default demo view

# --- Application Layout ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Raw Input Data")
    st.dataframe(raw_df, use_container_width=True)
    st.caption(f"Total Rows: {len(raw_df)} | Missing Values: {raw_df.isna().sum().sum()}")

# Process Data
clean_df = clean_and_impute_data(raw_df)

with col2:
    st.subheader("✨ Cleaned & Imputed Data")
    st.dataframe(clean_df, use_container_width=True)
    st.caption("Missing values imputed; category formats standardized.")

st.divider()

# --- Summary Statistics Milestone ---
st.subheader("📊 Category Metrics Summary")

summary_metrics = clean_df.groupby('Category')['Revenue'].agg(
    Min_Revenue='min',
    Max_Revenue='max',
    Mean_Revenue='mean',
    Total_Revenue='sum',
    Transaction_Count='count'
).reset_index()

# Display formatted KPI summary table
st.dataframe(
    summary_metrics.style.format({
        'Min_Revenue': '${:,.2f}',
        'Max_Revenue': '${:,.2f}',
        'Mean_Revenue': '${:,.2f}',
        'Total_Revenue': '${:,.2f}'
    }),
    use_container_width=True
)

st.divider()

# --- Interactive Visual Analytics ---
st.subheader("📈 Revenue Distribution Analytics")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    # Interactive Category Bar Chart (Plotly)
    fig_bar = px.bar(
        summary_metrics,
        x='Category',
        y='Total_Revenue',
        color='Category',
        title="Total Revenue per Category",
        text_auto='.2s'
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with chart_col2:
    # Revenue Distribution Box Plot (Matplotlib/Seaborn alternative via Plotly)
    fig_box = px.box(
        clean_df,
        x='Category',
        y='Revenue',
        color='Category',
        points="all",
        title="Revenue Distribution & Outliers by Category"
    )
    st.plotly_chart(fig_box, use_container_width=True)