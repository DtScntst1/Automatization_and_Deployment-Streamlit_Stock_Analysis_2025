import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

st.set_page_config(
    page_title="Stock Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
    }
    
    .info-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin-top: 10px;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 4px solid #2c3e50;
    }
    
    .info-card h3 {
        color: #2c3e50;
        margin-top: 0;
        font-size: 1.3rem;
    }
    
    .positive {
        color: #27ae60;
    }
    
    .negative {
        color: #e74c3c;
    }
    
    .sidebar .sidebar-content {
        background: #2c3e50;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

###########################
# Auxiliary Functions
###########################
def calculate_rsi(data, periods=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

###########################
# Sidebar Parameters
###########################
with st.sidebar:
    st.header("Analysis Parameters")
    ticker = st.text_input("Stock Symbol", "ASELS.IS")
    start_date = st.date_input("Start Date", datetime(2020, 1, 1))
    end_date = st.date_input("End Date", datetime.today())
    ma_short = st.number_input("Short MA Period", min_value=1, max_value=100, value=20)
    ma_long = st.number_input("Long MA Period", min_value=1, max_value=200, value=50)
    
    if st.button("Start Analysis", type="primary", use_container_width=True):
        try:
            data = yf.download(ticker, start=start_date, end=end_date)
            if data.empty:
                st.error("No data found. Please enter a valid symbol.")
            else:
                data = data.reset_index()
                data_new = data[['Date', 'Close', 'Volume']].copy()
                data_new.columns = ['Date', 'Close', 'Volume']
                data_new['Date'] = pd.to_datetime(data_new['Date'])
                
                data_new['MA_Short'] = data_new['Close'].rolling(ma_short).mean()
                data_new['MA_Long'] = data_new['Close'].rolling(ma_long).mean()
                data_new['RSI'] = calculate_rsi(data_new)
                
                st.session_state.data = data_new
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

###########################
# Main Title
###########################
st.title("📈 Stock Analysis")
st.markdown("---")

###########################
# Company Information
###########################
st.subheader("🏢 About Aselsan")
st.markdown("""
Aselsan is a leading Turkish defense electronics company, established in 1975. It is known for its advanced technology solutions in the fields of communication, radar, electronic warfare, electro-optics, and defense systems. Aselsan plays a crucial role in Turkey's defense industry, providing innovative products and services to both domestic and international markets.
""")

###########################
# Technical Analysis Dashboard
###########################
if 'data' in st.session_state:
    data_new = st.session_state.data

    row1_col1, row1_col2 = st.columns(2)
    
    with row1_col1:
        fig_price = go.Figure()
        fig_price.add_trace(go.Scatter(
            x=data_new['Date'],
            y=data_new['Close'],
            name='Close',
            line=dict(color='#3498db'),
            fill='tozeroy',  # Fill to the x-axis
            fillcolor='rgba(52, 152, 219, 0.2)'  # Light blue fill
        ))
        fig_price.add_trace(go.Scatter(
            x=data_new['Date'],
            y=data_new['MA_Short'],
            name=f'{ma_short} Day MA',
            line=dict(color='#e74c3c', dash='dot')
        ))
        fig_price.add_trace(go.Scatter(
            x=data_new['Date'],
            y=data_new['MA_Long'],
            name=f'{ma_long} Day MA',
            line=dict(color='#2ecc71', dash='dot')
        ))
        fig_price.update_layout(
            title='Closing Price and Moving Averages',
            xaxis_title='Date',
            yaxis_title='Price (TL)',
            template='plotly_white'
        )
        st.plotly_chart(fig_price, use_container_width=True)

        latest_price = data_new['Close'].iloc[-1]
        ma_short_value = data_new['MA_Short'].iloc[-1]
        ma_long_value = data_new['MA_Long'].iloc[-1]
        trend = "Rise" if ma_short_value > ma_long_value else "Drop"
        trend_color = "#27ae60" if ma_short_value > ma_long_value else "#e74c3c"
        st.markdown(f"""
        <div class="info-card">
            <h3>📈 Latest Price Information</h3>
            <p style="font-size: 24px; color: {trend_color};">{latest_price:.2f} TL</p>
            <p>{ma_short} Day MA: {ma_short_value:.2f}</p>
            <p>{ma_long} Day MA: {ma_long_value:.2f}</p>
            <p>Trend: <span style="color: {trend_color};">{trend}</span></p>
            <p style="font-style: italic;">(Closing price and moving averages chart)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with row1_col2:
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(
            x=data_new['Date'],
            y=data_new['RSI'],
            name='RSI',
            line=dict(color='#9b59b6'),
            fill='tozeroy',  # Fill to the x-axis
            fillcolor='rgba(155, 89, 182, 0.2)'  # Light purple fill
        ))
        fig_rsi.update_layout(
            title='Relative Strength Index (RSI)',
            yaxis_range=[0, 100],
            xaxis_title='Date',
            yaxis_title='RSI',
            template='plotly_white'
        )
        fig_rsi.add_hrect(y0=70, y1=100, line_width=0, fillcolor="red", opacity=0.1)
        fig_rsi.add_hrect(y0=0, y1=30, line_width=0, fillcolor="green", opacity=0.1)
        st.plotly_chart(fig_rsi, use_container_width=True)
        
        latest_rsi = data_new['RSI'].iloc[-1]
        rsi_status = "Overbought" if latest_rsi > 70 else ("Oversold" if latest_rsi < 30 else "Normal")
        rsi_color = "#e74c3c" if latest_rsi > 70 else ("#27ae60" if latest_rsi < 30 else "#2c3e50")
        st.markdown(f"""
        <div class="info-card">
            <h3>💹 RSI Status</h3>
            <p style="font-size: 24px; color: {rsi_color};">{latest_rsi:.1f}</p>
            <p>Status: {rsi_status}</p>
            <p style="font-style: italic;">(Determining overbought/oversold conditions with the RSI chart)</p>
        </div>
        """, unsafe_allow_html=True)

    ###########################
    # Volume Analysis
    ###########################
    st.subheader("📊 Volume Analysis")
    fig_volume = go.Figure()
    fig_volume.add_trace(go.Bar(
        x=data_new['Date'],
        y=data_new['Volume'],
        name='Volume',
        marker_color='#7f8c8d'
    ))
    fig_volume.update_layout(
        title='Trading Volume Over Time',
        xaxis_title='Date',
        yaxis_title='Volume',
        template='plotly_white'
    )
    st.plotly_chart(fig_volume, use_container_width=True)

    ###########################
    # Download Data
    ###########################
    st.subheader("📥 Download Data")
    csv = data_new.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name=f'{ticker}_data.csv',
        mime='text/csv',
    )

    ###########################
    # News Section
    ###########################
    st.subheader("📰 Recent News")
    # Placeholder for news - in a real application, you would fetch news from an API
    st.markdown("""
    - **[Aselsan Wins New Defense Contract](#)** - Aselsan has secured a new contract to supply advanced defense systems.
    - **[Innovations in Radar Technology](#)** - Aselsan unveils its latest radar technology at the defense expo.
    - **[Financial Results Q3 2023](#)** - Aselsan reports strong financial performance in the third quarter.
    """)

###########################
# Indicator Descriptions
###########################
with st.expander("📌 Indicator Descriptions"):
    st.markdown("""
    ****1. Closing Price and Moving Averages**
    - **Moving Averages (MA):** These are used to smooth out price data by creating a constantly updated average price. They help identify the direction of the trend.
    - **Short-term MA (e.g., 20-day):** This is more sensitive to price changes and can signal short-term trends. It is often used to identify potential buy or sell signals when it crosses above or below a longer-term MA.
    - **Long-term MA (e.g., 50-day):** This provides a broader view of the trend and is less sensitive to daily price fluctuations. It helps confirm the direction of the longer-term trend.
    - **Golden Cross:** Occurs when a short-term MA crosses above a long-term MA, indicating a potential upward trend.
    - **Death Cross:** Occurs when a short-term MA crosses below a long-term MA, indicating a potential downward trend.

    **2. RSI (Relative Strength Index)**
    - **RSI Overview:** The RSI is a momentum oscillator that measures the speed and change of price movements. It oscillates between 0 and 100.
    - **Overbought Condition (>70):** When the RSI is above 70, it suggests that the stock may be overbought or overvalued, potentially signaling a pullback or reversal.
    - **Oversold Condition (<30):** When the RSI is below 30, it suggests that the stock may be oversold or undervalued, potentially signaling a buying opportunity.
    - **Divergence:** Occurs when the price of a stock is moving in the opposite direction of the RSI. This can indicate a potential reversal.
    - **Centerline Crossover:** An RSI reading above 50 generally indicates an uptrend, while below 50 indicates a downtrend.

    **3. Volume Analysis**
    - **Volume Trends:** Volume is the number of shares traded during a given time period. It is an important indicator of market activity and liquidity.
    - **High Volume:** Often associated with strong price movements and can indicate the strength of a trend.
    - **Volume Spikes:** Sudden increases in volume can signal the beginning of a new trend or a reversal of an existing trend.
    - **Volume and Price Action:** When price moves are accompanied by high volume, it suggests that the move is more likely to be sustainable.

    These indicators are tools that can help traders and investors make informed decisions. However, they should be used in conjunction with other analysis methods and not as standalone signals.
    """)
st.markdown("---")
st.caption("© 2025 Stock Analysis Panel - All rights reserved.")




