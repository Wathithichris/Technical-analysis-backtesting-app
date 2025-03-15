import streamlit as st
import pandas as pd
import plotly.express as px
from backend import Returns
from treasury_yield import get_rf
from datetime import datetime


# set page layout to wide
st.set_page_config(layout='wide')

# Create title widget and description of the app
st.title("Stock Technical Analysis Backtester")
st.write("""This app is to backtest popular technical analysis strategies in the 
        stock market to get a feel of how they performed historically.""")

# Create ticker input widget to get stock ticker for pulling data
ticker = st.text_input("Stock ticker", placeholder='aapl')
ticker = ticker.strip().lower()


# Get current days date
today = datetime.today()

# Date inputs
start_date = st.date_input("Start date", key='start', format='YYYY-MM-DD', max_value=today)
end_date = st.date_input("End date", key='end', format='YYYY-MM-DD', max_value=today)

# Initialize session state for tracking error messages
if "messages" not in st.session_state:
    st.session_state.messages = []
else:
    st.session_state.messages.clear()

# Ensure valid date ranges
if end_date <= start_date:
    st.warning("Please enter a valid end date!")
    st.session_state.messages.append("Invalid end date!")

# Select strategy
strategy = st.selectbox("Select strategy", ('SMA crossover', 'Donchian Channel', 'EMA crossover'))

moving_averages = ['SMA crossover', 'EMA crossover']

# Strategy parameters
if strategy in moving_averages:
    short_ma = st.number_input("short moving average", key='ma_s', step=1)
    long_ma = st.number_input("long moving average", key='ma_l', step=1)

    if short_ma >= long_ma:
        st.warning("Please enter a valid short and long moving average period!")
        st.session_state.messages.append("Invalid moving averages!")


if strategy == 'Donchian Channel':
    period = st.number_input("Channel Period", key='period', step=1)
    if period <=0:
        st.warning("The channel period should be greater than 0!")
        st.session_state.messages.append("Invalid Donchian period!")

# Disable backtest button if warnings exist

backtest = st.button(label="Run backtest", disabled=len(st.session_state.messages)>0)

st.subheader("Backtest results")

# Run backtest if button is clicked
if backtest:
    try:
        if strategy in moving_averages:
            if strategy == 'SMA crossover':
                data = Returns(ticker=ticker, start_date=start_date, end_date=end_date, strategy=strategy,
                           sma_long=long_ma, sma_short=short_ma)
            elif strategy == 'EMA crossover':
                data = Returns(ticker=ticker, start_date=start_date, end_date=end_date, strategy=strategy,
                           ema_long=long_ma, ema_short=short_ma)

        elif strategy=="Donchian Channel":
            data = Returns(ticker=ticker, start_date=start_date, end_date=end_date, strategy=strategy,
                         donchian_period=period)

        stats = None
        if data:
            stats = pd.DataFrame(Returns.strategy_stats(data.calculate()['log_returns']), index=['Buy_and_hold'])
            stats = pd.concat([stats, pd.DataFrame(Returns.strategy_stats(data.calculate()['strategy_log_returns']),
                                                   index=['Strategy_returns'])])

    except Exception as e:
        match e:
            case ValueError():
                st.write("Oops!, please enter a valid ticker")

    else:
        # Create figure object
        figure = data.visualize()

        # Visualize closing prices of the stock
        st.plotly_chart(figure_or_data=figure, height=1500, width=600)

        # Output stats dataframe
        st.dataframe(data=stats)

        # Get extensive backtest
        results = data.export(stats)

        # Download extensive results
        results_csv = results.to_csv(index=False).encode('utf-8').copy()
        st.download_button(label="Download results csv", data=results_csv,
                           file_name=f"{ticker}_{strategy}_backtest.csv")



