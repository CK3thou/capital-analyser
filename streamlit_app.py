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

def initialize_session_state():
    """Initialize session state variables"""
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'selected_category' not in st.session_state:
        st.session_state.selected_category = "All"
    if 'search_term' not in st.session_state:
        st.session_state.search_term = ""

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
    # Initialize session state
    initialize_session_state()
    
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
    
    # Filters (moved before metrics)
    st.markdown("---")
    
    col_filter1, col_filter2 = st.columns(2)
    
    # Always create widgets to avoid duplicate key errors
    with col_filter1:
        categories_list = ["All"] + sorted(df['Category'].unique().tolist()) if 'Category' in df.columns else ["All"]
        try:
            current_idx = categories_list.index(st.session_state.selected_category)
        except ValueError:
            current_idx = 0
        selected_cat = st.selectbox(
            "Filter by Category",
            categories_list,
            index=current_idx,
            key="category_filter_widget"
        )
        if selected_cat != st.session_state.selected_category:
            st.session_state.selected_category = selected_cat
    
    with col_filter2:
        search_input = st.text_input(
            "Search Markets", 
            placeholder="Enter market name or symbol...", 
            value=st.session_state.search_term, 
            key="search_filter_widget"
        )
        if search_input != st.session_state.search_term:
            st.session_state.search_term = search_input
    
    # Apply filters using session state
    filtered_df = df.copy()
    filtered_df_numeric = df_numeric.copy()
    
    if 'Category' in filtered_df.columns and st.session_state.selected_category != "All":
        mask = filtered_df['Category'] == st.session_state.selected_category
        filtered_df = filtered_df[mask]
        filtered_df_numeric = filtered_df_numeric[mask]
    
    if st.session_state.search_term:
        mask = (filtered_df['Name'].str.contains(st.session_state.search_term, case=False, na=False) | 
                filtered_df['Symbol'].str.contains(st.session_state.search_term, case=False, na=False))
        filtered_df = filtered_df[mask]
        filtered_df_numeric = filtered_df_numeric[mask]
    
    # Statistics Dashboard (using filtered data)
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Markets", len(filtered_df))
    
    with col2:
        if st.session_state.selected_category == "All":
            categories = filtered_df['Category'].nunique() if 'Category' in filtered_df.columns else 0
            st.metric("Categories", categories)
        else:
            # Show category name when filtered
            st.metric("Category", st.session_state.selected_category)
    
    with col3:
        if 'Perf % 1M' in filtered_df_numeric.columns:
            top_perf = filtered_df_numeric['Perf % 1M'].max()
            st.metric("Best Monthly Return", f"{top_perf:.2f}%" if pd.notna(top_perf) and not np.isinf(top_perf) else "N/A")
        else:
            st.metric("Best Monthly Return", "N/A")
    
    with col4:
        if 'Price Change %' in filtered_df_numeric.columns:
            try:
                avg_change = filtered_df_numeric['Price Change %'].mean()
                st.metric("Avg Price Change", f"{avg_change:.2f}%" if pd.notna(avg_change) and not np.isinf(avg_change) else "N/A")
            except (TypeError, ValueError):
                st.metric("Avg Price Change", "N/A")
        else:
            st.metric("Avg Price Change", "N/A")
    
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
                    st.plotly_chart(fig, width='stretch')
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
            st.plotly_chart(fig, width='stretch')
    
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
            st.plotly_chart(fig, width='stretch')
    
    # Top/Bottom performers
    st.markdown("---")
    st.markdown("### 🏆 Top Performers by Category")
    
    # Create tabs for different timeframes
    tab_1w, tab_1m, tab_3m, tab_1y = st.tabs(["1 Week", "1 Month", "3 Months", "1 Year"])
    
    def show_top_by_category(perf_col):
        """Show top performer from each category"""
        if perf_col in filtered_df_numeric.columns and 'Category' in filtered_df.columns:
            categories = filtered_df['Category'].unique()
            
            for category in sorted(categories):
                cat_mask = filtered_df['Category'] == category
                cat_data = filtered_df_numeric[cat_mask]
                
                if len(cat_data) > 0:
                    top_performer = cat_data.nlargest(1, perf_col)
                    if len(top_performer) > 0:
                        row = top_performer.iloc[0]
                        perf = row[perf_col]
                        if pd.notna(perf):
                            color_class = 'positive' if perf > 0 else 'negative'
                            st.write(f"**{category.upper()}**: {row['Name']} ({row['Symbol']}) - <span class='{color_class}'>{perf:.2f}%</span>", unsafe_allow_html=True)
    
    with tab_1w:
        st.markdown("#### 🚀 Top Performer in Each Category (1 Week)")
        show_top_by_category('Perf % 1W')
        
        st.markdown("---")
        st.markdown("#### 📊 Overall Top 5 Gainers & Losers")
        col_top, col_bot = st.columns(2)
        if 'Perf % 1W' in filtered_df_numeric.columns:
            with col_top:
                top_5 = filtered_df_numeric.nlargest(5, 'Perf % 1W')[['Name', 'Symbol', 'Perf % 1W']]
                st.markdown("**Top 5 Gainers**")
                for idx, (i, row) in enumerate(top_5.iterrows(), 1):
                    perf = row['Perf % 1W']
                    if pd.notna(perf):
                        st.write(f"{idx}. {row['Name']} ({row['Symbol']}): <span class='positive'>{perf:.2f}%</span>", unsafe_allow_html=True)
            
            with col_bot:
                bottom_5 = filtered_df_numeric.nsmallest(5, 'Perf % 1W')[['Name', 'Symbol', 'Perf % 1W']]
                st.markdown("**Top 5 Losers**")
                for idx, (i, row) in enumerate(bottom_5.iterrows(), 1):
                    perf = row['Perf % 1W']
                    if pd.notna(perf):
                        st.write(f"{idx}. {row['Name']} ({row['Symbol']}): <span class='negative'>{perf:.2f}%</span>", unsafe_allow_html=True)
    
    with tab_1m:
        st.markdown("#### 🚀 Top Performer in Each Category (1 Month)")
        show_top_by_category('Perf % 1M')
        
        st.markdown("---")
        st.markdown("#### 📊 Overall Top 5 Gainers & Losers")
        col_top, col_bot = st.columns(2)
        if 'Perf % 1M' in filtered_df_numeric.columns:
            with col_top:
                top_5 = filtered_df_numeric.nlargest(5, 'Perf % 1M')[['Name', 'Symbol', 'Perf % 1M']]
                st.markdown("**Top 5 Gainers**")
                for idx, (i, row) in enumerate(top_5.iterrows(), 1):
                    perf = row['Perf % 1M']
                    if pd.notna(perf):
                        st.write(f"{idx}. {row['Name']} ({row['Symbol']}): <span class='positive'>{perf:.2f}%</span>", unsafe_allow_html=True)
            
            with col_bot:
                bottom_5 = filtered_df_numeric.nsmallest(5, 'Perf % 1M')[['Name', 'Symbol', 'Perf % 1M']]
                st.markdown("**Top 5 Losers**")
                for idx, (i, row) in enumerate(bottom_5.iterrows(), 1):
                    perf = row['Perf % 1M']
                    if pd.notna(perf):
                        st.write(f"{idx}. {row['Name']} ({row['Symbol']}): <span class='negative'>{perf:.2f}%</span>", unsafe_allow_html=True)
    
    with tab_3m:
        st.markdown("#### 🚀 Top Performer in Each Category (3 Months)")
        show_top_by_category('Perf % 3M')
        
        st.markdown("---")
        st.markdown("#### 📊 Overall Top 5 Gainers & Losers")
        col_top, col_bot = st.columns(2)
        if 'Perf % 3M' in filtered_df_numeric.columns:
            with col_top:
                top_5 = filtered_df_numeric.nlargest(5, 'Perf % 3M')[['Name', 'Symbol', 'Perf % 3M']]
                st.markdown("**Top 5 Gainers**")
                for idx, (i, row) in enumerate(top_5.iterrows(), 1):
                    perf = row['Perf % 3M']
                    if pd.notna(perf):
                        st.write(f"{idx}. {row['Name']} ({row['Symbol']}): <span class='positive'>{perf:.2f}%</span>", unsafe_allow_html=True)
            
            with col_bot:
                bottom_5 = filtered_df_numeric.nsmallest(5, 'Perf % 3M')[['Name', 'Symbol', 'Perf % 3M']]
                st.markdown("**Top 5 Losers**")
                for idx, (i, row) in enumerate(bottom_5.iterrows(), 1):
                    perf = row['Perf % 3M']
                    if pd.notna(perf):
                        st.write(f"{idx}. {row['Name']} ({row['Symbol']}): <span class='negative'>{perf:.2f}%</span>", unsafe_allow_html=True)
    
    with tab_1y:
        st.markdown("#### 🚀 Top Performer in Each Category (1 Year)")
        show_top_by_category('Perf % 1Y')
        
        st.markdown("---")
        st.markdown("#### 📊 Overall Top 5 Gainers & Losers")
        col_top, col_bot = st.columns(2)
        if 'Perf % 1Y' in filtered_df_numeric.columns:
            with col_top:
                top_5 = filtered_df_numeric.nlargest(5, 'Perf % 1Y')[['Name', 'Symbol', 'Perf % 1Y']]
                st.markdown("**Top 5 Gainers**")
                for idx, (i, row) in enumerate(top_5.iterrows(), 1):
                    perf = row['Perf % 1Y']
                    if pd.notna(perf):
                        st.write(f"{idx}. {row['Name']} ({row['Symbol']}): <span class='positive'>{perf:.2f}%</span>", unsafe_allow_html=True)
            
            with col_bot:
                bottom_5 = filtered_df_numeric.nsmallest(5, 'Perf % 1Y')[['Name', 'Symbol', 'Perf % 1Y']]
                st.markdown("**Top 5 Losers**")
                for idx, (i, row) in enumerate(bottom_5.iterrows(), 1):
                    perf = row['Perf % 1Y']
                    if pd.notna(perf):
                        st.write(f"{idx}. {row['Name']} ({row['Symbol']}): <span class='negative'>{perf:.2f}%</span>", unsafe_allow_html=True)
    
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
            st.plotly_chart(fig, width='stretch')
        if 'Currency' in filtered_df.columns:
            currency_dist = filtered_df['Currency'].value_counts().head(10)
            fig = px.bar(
                x=currency_dist.index,
                y=currency_dist.values,
                title="Top 10 Currencies",
                labels={'x': 'Currency', 'y': 'Count'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, width='stretch')
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
