import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ta.momentum import RSIIndicator
from ta.trend import MACD
from ta.volatility import BollingerBands
import datetime

# -------------------- CONFIG --------------------
EMAIL_ADDRESS = 'your_email@gmail.com'
EMAIL_PASSWORD = 'your_password'
WHATSAPP_WEBHOOK_URL = ''  # Placeholder if using Twilio or CallMeBot

# -------------------- TITLE --------------------
st.set_page_config(page_title="📈 Smart Stock Signal Advisor")
st.title("📊 Stock Analysis & Signal Generator")
st.markdown("Developed by **Ahmad Ahsan Akbar**  |  [🌐 Website](https://ahmad-ahsan-akbar.me)  |  [📘 Facebook](https://facebook.com/ahmadahsanakbar)")

# -------------------- FILE UPLOAD --------------------
st.sidebar.header("📁 Upload CSV File")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type=["csv"])

# -------------------- SAMPLE CSV --------------------
import os

# Read the sample CSV file
with open("sample_stock_data.csv", "rb") as file:
    sample_bytes = file.read()

# Add a download button in the sidebar or main area
st.sidebar.download_button(
    label="📥 Download Sample CSV",
    data=sample_bytes,
    file_name="sample_stock_data.csv",
    mime="text/csv"
)


# -------------------- APP LOGIC --------------------
if uploaded_file:
    data = pd.read_csv(uploaded_file)
    data['Date'] = pd.to_datetime(data['Date'])
    data = data.sort_values('Date')

    # Sliders for MA windows
    short_window = st.sidebar.slider("Short Moving Average", min_value=3, max_value=50, value=5)
    long_window = st.sidebar.slider("Long Moving Average", min_value=10, max_value=200, value=20)

    # Moving Averages
    data['Short_MA'] = data['Close'].rolling(window=short_window).mean()
    data['Long_MA'] = data['Close'].rolling(window=long_window).mean()

    # RSI
    data['RSI'] = RSIIndicator(close=data['Close'], window=14).rsi()

    # MACD
    macd = MACD(close=data['Close'])
    data['MACD'] = macd.macd()
    data['MACD_Signal'] = macd.macd_signal()

    # Bollinger Bands
    bb = BollingerBands(close=data['Close'])
    data['BB_High'] = bb.bollinger_hband()
    data['BB_Low'] = bb.bollinger_lband()

    # Signal Generation
    data['Signal'] = 0
    data.loc[(data['Short_MA'] > data['Long_MA']) & (data['Short_MA'].shift(1) <= data['Long_MA'].shift(1)), 'Signal'] = 1  # Buy
    data.loc[(data['Short_MA'] < data['Long_MA']) & (data['Short_MA'].shift(1) >= data['Long_MA'].shift(1)), 'Signal'] = -1  # Sell
    data['Position'] = data['Signal'].cumsum()

    # Visual Chart
    st.subheader("📈 Stock Price & Trading Signals")
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(data['Date'], data['Close'], label='Close Price', color='lightgray')
    ax.plot(data['Date'], data['Short_MA'], label=f'Short MA ({short_window})', color='blue')
    ax.plot(data['Date'], data['Long_MA'], label=f'Long MA ({long_window})', color='red')
    ax.plot(data['Date'], data['BB_High'], label='BB High', linestyle='--', alpha=0.3)
    ax.plot(data['Date'], data['BB_Low'], label='BB Low', linestyle='--', alpha=0.3)
    ax.scatter(data.loc[data['Signal'] == 1]['Date'], data.loc[data['Signal'] == 1]['Close'], label='Buy', marker='^', color='green', s=100)
    ax.scatter(data.loc[data['Signal'] == -1]['Date'], data.loc[data['Signal'] == -1]['Close'], label='Sell', marker='v', color='red', s=100)
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    # Latest Signal
    latest_signal = data['Signal'].iloc[-1]
    if latest_signal == 1:
        st.success("📈 Latest Signal: BUY")
    elif latest_signal == -1:
        st.error("🔻 Latest Signal: SELL")
    else:
        st.info("ℹ️ Latest Signal: No new signal")

    # Save results to CSV
    data.to_csv("stock_signal_results.csv", index=False)
    st.download_button("💾 Download Result CSV", data=data.to_csv(index=False), file_name="stock_signal_results.csv", mime='text/csv')

    # Email Alerts
    def send_email_alert(signal):
        subject = f"Stock Alert: {'BUY' if signal == 1 else 'SELL'}"
        body = f"Signal: {'BUY' if signal == 1 else 'SELL'}\n\nDate: {data['Date'].iloc[-1]}\nPrice: {data['Close'].iloc[-1]}"
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = EMAIL_ADDRESS
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
            server.quit()
            st.success("✅ Email alert sent!")
        except Exception as e:
            st.warning(f"Email failed: {e}")

    if latest_signal in [1, -1]:
        send_email_alert(latest_signal)

    # WhatsApp Alerts (Placeholder)
    if WHATSAPP_WEBHOOK_URL:
        st.info("🔔 WhatsApp alert would be sent here (integrate with Twilio/CallMeBot)")

    # RSI / MACD Table
    st.subheader("📊 Technical Indicators")
    st.dataframe(data[['Date', 'RSI', 'MACD', 'MACD_Signal']].tail(10))

else:
    st.info("⬆️ Upload a CSV file to get started")
