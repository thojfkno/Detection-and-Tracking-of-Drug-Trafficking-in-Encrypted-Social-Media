import streamlit as st
import joblib
import numpy as np
import re
import pandas as pd
from datetime import datetime
from scipy.sparse import hstack
from scipy.sparse import hstack

# Load saved model
model = joblib.load("drug_detection_model.pkl")
vectorizer = joblib.load("vectorizer.pkl")

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"#", "", text)
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    return text

def slang_flag(text):
    strong_patterns = [
        "dm", "inbox", "private", "cash", "deal",
        "delivery", "stock", "price", "contact",
        "meet", "location"
    ]
    score = 0
    for word in strong_patterns:
        if word in text:
            score += 1
    return score

st.title("🚨 Drug Activity Detection Dashboard")

platform = st.selectbox(
    "Select Platform",
    ["WhatsApp", "Instagram", "Telegram", "Twitter"]
)

msg = st.text_input("Enter Message")

def context_correction(message, prediction):
    normal_words = [
        "family","dinner","lunch","breakfast","temple",
        "movie","friends","study","exam","office",
        "gym","music","walk","shopping","travel"
    ]

    msg = message.lower()

    if prediction == 1:
        if any(word in msg for word in normal_words):
            return 0
    return prediction
    
if st.button("Predict"):

    cleaned = clean_text(msg)
    vect = vectorizer.transform([cleaned])

    msg_length = len(cleaned)
    word_count = len(cleaned.split())
    hour_of_day = np.random.randint(0, 24)
    post_freq = np.random.randint(1, 20)
    slang = slang_flag(cleaned)
    
    behavior = np.array([[msg_length, word_count, hour_of_day, post_freq, slang * 3]])

    final_input = hstack([vect, behavior])

    raw_pred = model.predict(final_input)[0]
    pred = context_correction(msg, raw_pred)

    if pred == 1:
        st.error("🚨 Suspicious Message Detected")
    else:
        st.success("✅ Normal Message")
log = pd.DataFrame({
    "platform":[platform],
    "message":[msg],
    "prediction":[pred],
    "time":[datetime.now()]
})

log.to_csv("activity_log.csv", mode='a', header=False, index=False)

st.write("📊 Behavioral Analysis")
st.write("Message Length:", msg_length)
st.write("Posting Hour:", hour_of_day)
st.write("Post Freq:", post_freq)
st.subheader("📁 Activity Log")

try:
    log_df = pd.read_csv("activity_log.csv")
    st.dataframe(log_df.tail(10))
except:
    st.write("No activity yet")