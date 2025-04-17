import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import smtplib
from email.mime.text import MIMEText

# ========== ANALYSIS LOGIC ==========

def analyze_signals(df, short_window, long_window):
    df = df.copy()
    df['Short_MA'] = df['Close'].rolling(window=short_window).mean()
    df['Long_MA'] = df['Close'].rolling(window=long_window).mean()
    df['Signal'] = 0
    df['Signal'][short_window:] = (df['Short_MA'][short_window:] > df['Long_MA'][short_window:]).astype(int)
    df['Position'] = df['Signal'].diff()
    return df

def plot_signals(df):
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.plot(df['Close'], label='Close Price', alpha=0.5)
    ax.plot(df['Short_MA'], label='Short MA', color='blue')
    ax.plot(df['Long_MA'], label='Long MA', color='orange')

    buy_signals = df[df['Position'] == 1]
    sell_signals = df[df['Position'] == -1]

    ax.plot(buy_signals.index, buy_signals['Short_MA'], '^', markersize=10, color='green', label='Buy Signal')
    ax.plot(sell_signals.index, sell_signals['Short_MA'], 'v', markersize=10, color='red', label='Sell Signal')

    ax.set_title('Buy/Sell Signals Using Moving Averages')
    ax.legend()
    ax.grid(True)
    return fig

# ========== EMAIL LOGIC ==========

def send_email(subject, message, from_email, to_email, smtp_server, smtp_port, login, password):
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(login, password)
            server.sendmail(from_email, to_email, msg.as_string())
        return True
    except Exception as e:
        return str(e)

# ========== STREAMLIT UI ==========

st.set_page_config(page_title="Stock Signal Analyzer", layout="wide")
st.title("📈 Moving Average Stock Signal Generator")

uploaded_file = st.file_uploader("Upload a CSV file with 'Date' and 'Close' columns", type=['csv'])

if uploaded_file:
    df = pd.read_csv(uploaded_file, parse_dates=['Date'])
    df.sort_values('Date', inplace=True)
    df.set_index('Date', inplace=True)

    st.subheader("📊 Data Preview")
    st.write(df.head())

    st.sidebar.header("⚙️ Signal Settings")
    short_window = st.sidebar.slider("Short Moving Average", 3, 50, 20)
    long_window = st.sidebar.slider("Long Moving Average", 10, 200, 50)

    if short_window >= long_window:
        st.error("Short window must be less than long window.")
    else:
        df_signals = analyze_signals(df, short_window, long_window)

        st.subheader("📈 Buy/Sell Chart")
        st.pyplot(plot_signals(df_signals))

        st.subheader("📋 Signal Table")
        signal_df = df_signals[df_signals['Position'].isin([1, -1])]
        signal_df['Signal Type'] = signal_df['Position'].map({1: 'Buy', -1: 'Sell'})
        st.write(signal_df[['Close', 'Short_MA', 'Long_MA', 'Signal Type']])

        st.subheader("📥 Download Signals as CSV")
        csv_data = signal_df[['Close', 'Short_MA', 'Long_MA', 'Signal Type']]
        st.download_button(
            label="Download CSV",
            data=csv_data.to_csv().encode('utf-8'),
            file_name='stock_signals.csv',
            mime='text/csv'
        )

        st.subheader("📧 Send Email Alert")
        with st.form("email_form"):
            from_email = st.text_input("Sender Email")
            to_email = st.text_input("Recipient Email")
            smtp_server = st.text_input("SMTP Server", value="smtp.gmail.com")
            smtp_port = st.number_input("SMTP Port", value=587)
            login = st.text_input("SMTP Login (usually your email)")
            password = st.text_input("SMTP Password or App Password", type="password")
            submit_email = st.form_submit_button("Send Email")

        if submit_email:
            signal_message = signal_df[['Close', 'Signal Type']].to_string()
            subject = "📈 Stock Trading Signals"
            result = send_email(subject, signal_message, from_email, to_email, smtp_server, smtp_port, login, password)
            if result is True:
                st.success("✅ Email sent successfully.")
            else:
                st.error(f"❌ Failed to send email: {result}")
