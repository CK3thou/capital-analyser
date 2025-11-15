"""
Capital.com Market Analyzer - Streamlit Web App
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="Capital.com Market Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .positive {
        color: #00D084;
        font-weight: bold;
    }
    .negative {
        color: #FF4B4B;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_market_data():
    """Load market data from CSV file"""
    csv_file = 'capital_markets_analysis.csv'
    
    if not os.path.exists(csv_file):
        return None
    
    try:
        df = pd.read_csv(csv_file)
        return df
    except Exception as e:
        st.error(f"Error loading CSV: {str(e)}")
        return None

def parse_percentage(value):
    """Parse percentage string to float"""
    if pd.isna(value):
        return np.nan
    if isinstance(value, str):
        try:
            return float(value.replace('%', '').strip())
        except (ValueError, AttributeError):
            return np.nan
    return float(value)

def format_perf_columns(df):
    """Convert performance string columns to numeric for calculations"""
    df_numeric = df.copy()
    # Convert all percentage columns (Perf % and Price Change %)
    percentage_cols = [col for col in df_numeric.columns if '%' in col]
    for col in percentage_cols:
        if col in df_numeric.columns:
            df_numeric[col] = df_numeric[col].apply(parse_percentage)
    return df_numeric

def main():
    # Header
    st.title("📊 Capital.com Market Analyzer")
    st.markdown("Real-time market performance tracking across multiple asset classes")
    
    # Load data
    df = load_market_data()
    
    if df is None or len(df) == 0:
        st.warning("⚠️ No data available")
        st.info("""
        ### To populate data:
        1. Configure your API credentials in `config.py`
        2. Run `python run_analyzer.py` to fetch market data
        3. This will create `capital_markets_analysis.csv`
        4. Refresh this page to see the data
        """)
        return
    
    # Convert performance columns to numeric for calculations
    df_numeric = format_perf_columns(df)
    
    # Statistics Dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Markets", len(df))
    
    with col2:
        categories = df['Category'].nunique() if 'Category' in df.columns else 0
        st.metric("Categories", categories)
    
    with col3:
        if 'Perf % 1M' in df_numeric.columns:
            top_perf = df_numeric['Perf % 1M'].max()
            st.metric("Best Monthly Return", f"{top_perf:.2f}%" if pd.notna(top_perf) and not np.isinf(top_perf) else "N/A")
    
    with col4:
        if 'Price Change %' in df_numeric.columns:
            try:
                avg_change = df_numeric['Price Change %'].mean()
                st.metric("Avg Price Change", f"{avg_change:.2f}%" if pd.notna(avg_change) and not np.isinf(avg_change) else "N/A")
            except (TypeError, ValueError):
                st.metric("Avg Price Change", "N/A")
    
    # Filters
    st.markdown("---")
    
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    
    with col_filter1:
        if 'Category' in df.columns:
            categories_list = sorted(df['Category'].unique())
            selected_category = st.selectbox(
                "Filter by Category",
                ["All"] + categories_list,
                key="category_filter"
            )
        else:
            selected_category = "All"
    
    with col_filter2:
        search_term = st.text_input("Search Markets", placeholder="Enter market name or symbol...", key="search_filter")
    
    with col_filter3:
        if 'Type' in df.columns:
            types_list = sorted(df['Type'].dropna().unique())
            selected_type = st.selectbox(
                "Filter by Type",
                ["All"] + types_list if len(types_list) > 0 else ["All"],
                key="type_filter"
            )
        else:
            selected_type = "All"
    
    # Apply filters
    filtered_df = df.copy()
    filtered_df_numeric = df_numeric.copy()
    
    if 'Category' in filtered_df.columns and selected_category != "All":
        mask = filtered_df['Category'] == selected_category
        filtered_df = filtered_df[mask]
        filtered_df_numeric = filtered_df_numeric[mask]
    
    if search_term:
        mask = (filtered_df['Name'].str.contains(search_term, case=False, na=False) | 
                filtered_df['Symbol'].str.contains(search_term, case=False, na=False))
        filtered_df = filtered_df[mask]
        filtered_df_numeric = filtered_df_numeric[mask]
    
    if 'Type' in filtered_df.columns and selected_type != "All":
        mask = filtered_df['Type'] == selected_type
        filtered_df = filtered_df[mask]
        filtered_df_numeric = filtered_df_numeric[mask]
    
    # Define all columns from run_analyzer.py
    all_columns = [
        'Category', 'Symbol', 'Name', 'Current Price', 'Currency', 
        'Price Change %', 'Perf % 1W', 'Perf % 1M', 'Perf % 3M', 
        'Perf % 6M', 'Perf % YTD', 'Perf % 1Y', 'Perf % 5Y', 
        'Perf % 10Y', 'Market Status', 'Type'
    ]
    
    # Get available columns
    available_cols = [col for col in all_columns if col in filtered_df.columns]
    
    # Display data table
    st.markdown(f"### 📋 Markets Data ({len(filtered_df)} results)")
    
    display_df = filtered_df[available_cols].copy()
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Performance Analysis Charts
    st.markdown("---")
    st.markdown("### 📈 Performance Analysis")
    
    # Get performance columns
    perf_columns = [col for col in filtered_df_numeric.columns if col.startswith('Perf %')]
    
    # Chart 1: Average performance by category
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        if 'Perf % 1M' in filtered_df_numeric.columns and 'Category' in filtered_df.columns:
            try:
                perf_by_cat = filtered_df_numeric.groupby(filtered_df['Category'])['Perf % 1M'].mean().sort_values(ascending=False)
                perf_by_cat = perf_by_cat[perf_by_cat.notna()]  # Remove NaN values
                if len(perf_by_cat) > 0:
                    fig = px.bar(
                        x=perf_by_cat.values,
                        y=perf_by_cat.index,
                        title="Avg 1-Month Performance by Category",
                        labels={'x': 'Performance (%)', 'y': 'Category'},
                        orientation='h',
                        color=perf_by_cat.values,
                        color_continuous_scale=['#FF4B4B', '#FFD700', '#00D084']
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning("Could not generate category performance chart")
    
    with col_chart2:
        if 'Category' in filtered_df.columns:
            category_counts = filtered_df['Category'].value_counts()
            fig = px.pie(
                values=category_counts.values,
                names=category_counts.index,
                title="Markets Distribution by Category"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    # Chart 3: Performance comparison across timeframes
    st.markdown("### ⏱️ Multi-Timeframe Performance Comparison")
    
    if perf_columns:
        # Calculate average performance for each timeframe
        timeframe_avg = {}
        for col in perf_columns:
            try:
                avg_val = pd.to_numeric(filtered_df_numeric[col], errors='coerce').mean()
                if pd.notna(avg_val) and not np.isinf(avg_val):
                    timeframe_avg[col.replace('Perf % ', '')] = avg_val
            except:
                pass
        
        if timeframe_avg:
            timeframe_df = pd.DataFrame(list(timeframe_avg.items()), columns=['Timeframe', 'Avg Performance'])
            
            fig = px.bar(
                timeframe_df,
                x='Timeframe',
                y='Avg Performance',
                title="Average Performance Across All Timeframes",
                color='Avg Performance',
                color_continuous_scale=['#FF4B4B', '#FFD700', '#00D084'],
                labels={'Avg Performance': 'Performance (%)'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    # Top/Bottom performers for multiple timeframes
    st.markdown("---")
    st.markdown("### 🏆 Top & Bottom Performers")
    
    # Create tabs for different timeframes
    tab_1w, tab_1m, tab_3m, tab_1y = st.tabs(["1 Week", "1 Month", "3 Months", "1 Year"])
    
    with tab_1w:
        col_top, col_bot = st.columns(2)
        if 'Perf % 1W' in filtered_df_numeric.columns:
            with col_top:
                top_5 = filtered_df_numeric.nlargest(5, 'Perf % 1W')[['Name', 'Symbol', 'Perf % 1W']]
                st.markdown("#### 🚀 Top 5 Gainers")
                for idx, (i, row) in enumerate(top_5.iterrows(), 1):
                    perf = row['Perf % 1W']
                    if pd.notna(perf):
                        st.write(f"**{idx}. {row['Name']}** ({row['Symbol']}): <span class='positive'>{perf:.2f}%</span>", unsafe_allow_html=True)
            
            with col_bot:
                bottom_5 = filtered_df_numeric.nsmallest(5, 'Perf % 1W')[['Name', 'Symbol', 'Perf % 1W']]
                st.markdown("#### 📉 Top 5 Losers")
                for idx, (i, row) in enumerate(bottom_5.iterrows(), 1):
                    perf = row['Perf % 1W']
                    if pd.notna(perf):
                        st.write(f"**{idx}. {row['Name']}** ({row['Symbol']}): <span class='negative'>{perf:.2f}%</span>", unsafe_allow_html=True)
    
    with tab_1m:
        col_top, col_bot = st.columns(2)
        if 'Perf % 1M' in filtered_df_numeric.columns:
            with col_top:
                top_5 = filtered_df_numeric.nlargest(5, 'Perf % 1M')[['Name', 'Symbol', 'Perf % 1M']]
                st.markdown("#### 🚀 Top 5 Gainers")
                for idx, (i, row) in enumerate(top_5.iterrows(), 1):
                    perf = row['Perf % 1M']
                    if pd.notna(perf):
                        st.write(f"**{idx}. {row['Name']}** ({row['Symbol']}): <span class='positive'>{perf:.2f}%</span>", unsafe_allow_html=True)
            
            with col_bot:
                bottom_5 = filtered_df_numeric.nsmallest(5, 'Perf % 1M')[['Name', 'Symbol', 'Perf % 1M']]
                st.markdown("#### 📉 Top 5 Losers")
                for idx, (i, row) in enumerate(bottom_5.iterrows(), 1):
                    perf = row['Perf % 1M']
                    if pd.notna(perf):
                        st.write(f"**{idx}. {row['Name']}** ({row['Symbol']}): <span class='negative'>{perf:.2f}%</span>", unsafe_allow_html=True)
    
    with tab_3m:
        col_top, col_bot = st.columns(2)
        if 'Perf % 3M' in filtered_df_numeric.columns:
            with col_top:
                top_5 = filtered_df_numeric.nlargest(5, 'Perf % 3M')[['Name', 'Symbol', 'Perf % 3M']]
                st.markdown("#### 🚀 Top 5 Gainers")
                for idx, (i, row) in enumerate(top_5.iterrows(), 1):
                    perf = row['Perf % 3M']
                    if pd.notna(perf):
                        st.write(f"**{idx}. {row['Name']}** ({row['Symbol']}): <span class='positive'>{perf:.2f}%</span>", unsafe_allow_html=True)
            
            with col_bot:
                bottom_5 = filtered_df_numeric.nsmallest(5, 'Perf % 3M')[['Name', 'Symbol', 'Perf % 3M']]
                st.markdown("#### 📉 Top 5 Losers")
                for idx, (i, row) in enumerate(bottom_5.iterrows(), 1):
                    perf = row['Perf % 3M']
                    if pd.notna(perf):
                        st.write(f"**{idx}. {row['Name']}** ({row['Symbol']}): <span class='negative'>{perf:.2f}%</span>", unsafe_allow_html=True)
    
    with tab_1y:
        col_top, col_bot = st.columns(2)
        if 'Perf % 1Y' in filtered_df_numeric.columns:
            with col_top:
                top_5 = filtered_df_numeric.nlargest(5, 'Perf % 1Y')[['Name', 'Symbol', 'Perf % 1Y']]
                st.markdown("#### 🚀 Top 5 Gainers")
                for idx, (i, row) in enumerate(top_5.iterrows(), 1):
                    perf = row['Perf % 1Y']
                    if pd.notna(perf):
                        st.write(f"**{idx}. {row['Name']}** ({row['Symbol']}): <span class='positive'>{perf:.2f}%</span>", unsafe_allow_html=True)
            
            with col_bot:
                bottom_5 = filtered_df_numeric.nsmallest(5, 'Perf % 1Y')[['Name', 'Symbol', 'Perf % 1Y']]
                st.markdown("#### 📉 Top 5 Losers")
                for idx, (i, row) in enumerate(bottom_5.iterrows(), 1):
                    perf = row['Perf % 1Y']
                    if pd.notna(perf):
                        st.write(f"**{idx}. {row['Name']}** ({row['Symbol']}): <span class='negative'>{perf:.2f}%</span>", unsafe_allow_html=True)
    
    # Market Status Distribution
    st.markdown("---")
    st.markdown("### 🔍 Market Status Analysis")
    
    col_status1, col_status2 = st.columns(2)
    
    with col_status1:
        if 'Market Status' in filtered_df.columns:
            status_dist = filtered_df['Market Status'].value_counts()
            fig = px.bar(
                x=status_dist.index,
                y=status_dist.values,
                title="Markets by Status",
                labels={'x': 'Status', 'y': 'Count'},
                color=status_dist.index
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col_status2:
        if 'Currency' in filtered_df.columns:
            currency_dist = filtered_df['Currency'].value_counts().head(10)
            fig = px.bar(
                x=currency_dist.index,
                y=currency_dist.values,
                title="Top 10 Currencies",
                labels={'x': 'Currency', 'y': 'Count'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    # Info
    st.markdown("---")
    st.markdown("""
    ### About
    This dashboard displays market analysis data fetched from the Capital.com API.
    - **Data**: Fetched from Capital.com REST API
    - **Categories**: Commodities, Forex, Indices, Cryptocurrencies, Shares/ETFs
    - **Metrics**: 1W, 1M, 3M, 6M, YTD, 1Y, 5Y, 10Y performance
    - **Columns**: Category, Symbol, Name, Price, Currency, Performance, Status, Type
    """)

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
