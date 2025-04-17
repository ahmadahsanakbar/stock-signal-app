import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from io import StringIO

# Configure the page
st.set_page_config(
    page_title="Stock Signal Analyzer by Ahmad",
    page_icon="📈",
    layout="wide"
)

# Branding Header
st.title("📊 Stock Signal Analyzer")
st.caption("Developed by Ahmad")

# File uploader
uploaded_file = st.file_uploader("Upload CSV file with Date and Close columns", type=["csv"])

# Email configuration
EMAIL_ADDRESS = st.secrets.get("EMAIL_ADDRESS", "")  # Put in Streamlit secrets for security
EMAIL_PASSWORD = st.secrets.get("EMAIL_PASSWORD", "")

# Moving Average function
def generate_signals(df, short_window=20, long_window=50):
    df["Short_MA"] = df["Close"].rolling(window=short_window).mean()
    df["Long_MA"] = df["Close"].rolling(window=long_window).mean()

    df["Signal"] = 0
    df["Signal"][short_window:] = np.where(df["Short_MA"][short_window:] > df["Long_MA"][short_window:], 1, -1)
    df["Position"] = df["Signal"].diff()

    return df

# Send email alert
def send_email(subject, body, to_email):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())

# Process file
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    try:
        df["Date"] = pd.to_datetime(df["Date"])
        df.sort_values("Date", inplace=True)
        df.reset_index(drop=True, inplace=True)

        # Generate signals
        df = generate_signals(df)

        # Display table
        st.subheader("Processed Stock Data")
        st.dataframe(df.tail(10))

        # Find and send alerts
        if df["Position"].iloc[-1] == 1:
            signal = "Buy Signal Triggered 📈"
        elif df["Position"].iloc[-1] == -1:
            signal = "Sell Signal Triggered 📉"
        else:
            signal = "No new signal."

        st.subheader("📢 Latest Signal")
        st.write(signal)

        # Optional email alert
        if signal != "No new signal.":
            to_email = st.text_input("Enter email to receive alert:")
            if st.button("Send Alert"):
                send_email("Stock Signal Alert", f"{signal} on {df['Date'].iloc[-1].date()}", to_email)
                st.success("Email alert sent!")

        # Export to CSV
        csv = df.to_csv(index=False)
        st.download_button("Download Processed CSV", csv, "processed_stock_data.csv", "text/csv")

    except Exception as e:
        st.error(f"Error: {e}")

# Footer with branding
st.markdown("""---""")
st.markdown(
    "<div style='text-align: center;'>"
    "📬 Developed with ❤️ by <b>Ahmad</b>"
    "</div>",
    unsafe_allow_html=True
)
