# Create file: optimized_dashboard.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import time

# Configure the page
st.set_page_config(
    page_title="Supply Chain Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Main title with custom styling
st.markdown('<h1 class="main-header">📊 Supply Chain Analytics Dashboard</h1>', unsafe_allow_html=True)

# Sidebar for filters
st.sidebar.header("🎛️ Dashboard Filters")

# Load data function with caching
@st.cache_data
def load_data():
    """Load and prepare the supply chain data"""
    df = pd.read_csv('supply_chain_data.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    return df

# Load the data
try:
    df = load_data()
    st.sidebar.success(f"✅ {len(df)} records loaded")
except FileNotFoundError:
    st.error("❌ Supply chain data file not found. Please run create_sample_data.py first.")
    st.stop()

# Sidebar filters
st.sidebar.subheader("Category & Supplier")
categories = ['All'] + sorted(df['Category'].unique().tolist())
selected_category = st.sidebar.selectbox("Product Category:", categories)

suppliers = ['All'] + sorted(df['Supplier'].unique().tolist())
selected_supplier = st.sidebar.selectbox("Supplier:", suppliers)

st.sidebar.subheader("Time Period")
months = ['All'] + sorted(df['Month'].unique().tolist(), reverse=True)
selected_month = st.sidebar.selectbox("Month:", months)

st.sidebar.subheader("Quality & Delivery")
quality_range = st.sidebar.slider(
    "Quality Score:",
    min_value=float(df['Quality_Score'].min()),
    max_value=float(df['Quality_Score'].max()),
    value=(float(df['Quality_Score'].min()), float(df['Quality_Score'].max())),
    step=0.1
)

delivery_range = st.sidebar.slider(
    "Delivery Days:",
    min_value=int(df['Delivery_Days'].min()),
    max_value=int(df['Delivery_Days'].max()),
    value=(int(df['Delivery_Days'].min()), int(df['Delivery_Days'].max()))
)

# Apply filters
@st.cache_data
def filter_data(df, category, supplier, month, quality_range, delivery_range):
    """Apply filters to the dataset"""
    filtered_df = df.copy()
    
    if category != 'All':
        filtered_df = filtered_df[filtered_df['Category'] == category]
    if supplier != 'All':
        filtered_df = filtered_df[filtered_df['Supplier'] == supplier]
    if month != 'All':
        filtered_df = filtered_df[filtered_df['Month'] == month]
    
    filtered_df = filtered_df[
        (filtered_df['Quality_Score'] >= quality_range[0]) & 
        (filtered_df['Quality_Score'] <= quality_range[1]) &
        (filtered_df['Delivery_Days'] >= delivery_range[0]) & 
        (filtered_df['Delivery_Days'] <= delivery_range[1])
    ]
    
    return filtered_df

filtered_df = filter_data(df, selected_category, selected_supplier, selected_month, quality_range, delivery_range)

# Main dashboard content
if len(filtered_df) > 0:
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📦 Total Orders", f"{filtered_df['Units_Ordered'].sum():,}")
    with col2:
        st.metric("🚚 Delivered", f"{filtered_df['Units_Delivered'].sum():,}")
    with col3:
        st.metric("⭐ Avg Quality", f"{filtered_df['Quality_Score'].mean():.2f}/10")
    with col4:
        st.metric("⏱️ Avg Delivery", f"{filtered_df['Delivery_Days'].mean():.1f} days")
    
    # Charts
    st.subheader("📊 Analytics")
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.subheader("Category Performance")
        category_data = filtered_df.groupby('Category')['Units_Ordered'].sum()
        fig1, ax1 = plt.subplots(figsize=(8, 6))
        category_data.plot(kind='bar', ax=ax1)
        ax1.set_title('Units Ordered by Category')
        plt.xticks(rotation=45)
        st.pyplot(fig1)
    
    with chart_col2:
        st.subheader("Quality Distribution")
        fig2, ax2 = plt.subplots(figsize=(8, 6))
        ax2.hist(filtered_df['Quality_Score'], bins=20, alpha=0.7)
        ax2.set_title('Quality Score Distribution')
        ax2.set_xlabel('Quality Score')
        ax2.set_ylabel('Frequency')
        st.pyplot(fig2)
    
    # Data summary
    with st.expander("📋 Data Summary"):
        st.write(f"**Records shown:** {len(filtered_df)}")
        st.write(f"**Date range:** {filtered_df['Date'].min().strftime('%Y-%m-%d')} to {filtered_df['Date'].max().strftime('%Y-%m-%d')}")
        st.dataframe(filtered_df.head(10))

else:
    st.warning("⚠️ No data matches your current filters. Please adjust the filter settings.")

# Performance info
st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip:** Use filters to explore different aspects of your supply chain data!")

