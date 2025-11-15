"""
Capital.com Market Analyzer - Streamlit Web App
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

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
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Markets", len(df))
    
    with col2:
        categories = df['Category'].nunique() if 'Category' in df.columns else 0
        st.metric("Categories", categories)
    
    with col3:
        if 'perf_1w' in df.columns:
            top_perf = df['perf_1w'].max()
            st.metric("Best Weekly Return", f"{top_perf:.2f}%" if pd.notna(top_perf) else "N/A")
    
    with col4:
        file_mod_time = datetime.fromtimestamp(os.path.getmtime('capital_markets_analysis.csv'))
        st.metric("Last Updated", file_mod_time.strftime('%Y-%m-%d %H:%M'))
    
    # Filters
    st.markdown("---")
    
    col_filter1, col_filter2 = st.columns(2)
    
    with col_filter1:
        if 'Category' in df.columns:
            categories = sorted(df['Category'].unique())
            selected_category = st.selectbox(
                "Filter by Category",
                ["All"] + categories
            )
    
    with col_filter2:
        search_term = st.text_input("Search Markets", placeholder="Enter market name...")
    
    # Apply filters
    filtered_df = df.copy()
    
    if 'Category' in filtered_df.columns and selected_category != "All":
        filtered_df = filtered_df[filtered_df['Category'] == selected_category]
    
    if search_term:
        filtered_df = filtered_df[
            filtered_df['instrumentName'].str.contains(search_term, case=False, na=False)
        ]
    
    # Display data
    st.markdown(f"### Markets ({len(filtered_df)} results)")
    
    # Performance columns to display
    perf_columns = [col for col in filtered_df.columns if col.startswith('perf_')]
    
    display_cols = ['instrumentName', 'Category']
    display_cols.extend(perf_columns)
    
    # Ensure all display columns exist
    display_cols = [col for col in display_cols if col in filtered_df.columns]
    
    # Format performance columns
    display_df = filtered_df[display_cols].copy()
    for col in perf_columns:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(
                lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A"
            )
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Charts
    st.markdown("---")
    st.markdown("### Performance Analysis")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        if 'perf_1m' in df.columns and 'Category' in df.columns:
            perf_by_category = df.groupby('Category')['perf_1m'].mean().sort_values(ascending=False)
            fig = px.bar(
                x=perf_by_category.values,
                y=perf_by_category.index,
                title="Average 1-Month Performance by Category",
                labels={'x': 'Performance (%)', 'y': 'Category'},
                orientation='h'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col_chart2:
        if 'Category' in df.columns:
            category_counts = df['Category'].value_counts()
            fig = px.pie(
                values=category_counts.values,
                names=category_counts.index,
                title="Markets by Category"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Top/Bottom performers
    st.markdown("---")
    col_top1, col_top2 = st.columns(2)
    
    with col_top1:
        if 'perf_1m' in df.columns:
            top_5 = df.nlargest(5, 'perf_1m')[['instrumentName', 'perf_1m']]
            st.markdown("#### 🚀 Top 5 Performers (1M)")
            for idx, row in top_5.iterrows():
                perf = row['perf_1m']
                if pd.notna(perf):
                    st.write(f"• **{row['instrumentName']}**: {perf:.2f}%")
    
    with col_top2:
        if 'perf_1m' in df.columns:
            bottom_5 = df.nsmallest(5, 'perf_1m')[['instrumentName', 'perf_1m']]
            st.markdown("#### 📉 Bottom 5 Performers (1M)")
            for idx, row in bottom_5.iterrows():
                perf = row['perf_1m']
                if pd.notna(perf):
                    st.write(f"• **{row['instrumentName']}**: {perf:.2f}%")
    
    # Info
    st.markdown("---")
    st.markdown("""
    ### About
    This dashboard displays market analysis data fetched from the Capital.com API.
    - **Data**: Fetched from Capital.com REST API
    - **Categories**: Commodities, Forex, Indices, Cryptocurrencies, Shares/ETFs
    - **Metrics**: 1W, 1M, 3M, 6M, YTD, 1Y, 5Y, 10Y performance
    """)

if __name__ == "__main__":
    main()
