import streamlit as st
import joblib
import sqlite3
from PIL import Image

# ---------------- DATABASE ----------------
conn = sqlite3.connect("history.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS history (
    followers INT,
    following INT,
    posts INT,
    bio_length INT,
    prediction TEXT,
    probability REAL
)
""")
conn.commit()

# ---------------- LOGIN ----------------
def login():
    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "1234":
            st.session_state["logged_in"] = True
        else:
            st.error("Invalid credentials")

# ---------------- MAIN APP ----------------
def main_app():
    model = joblib.load("model.pkl")

    st.title("🤖 AI Fake Profile Detector")

    st.sidebar.header("Profile Input")

    followers = st.sidebar.number_input("Followers", min_value=0)
    following = st.sidebar.number_input("Following", min_value=0)
    posts = st.sidebar.number_input("Posts", min_value=0)
    bio_length = st.sidebar.number_input("Bio Length", min_value=0)

    # IMAGE
    st.subheader("Upload Profile Image")
    image = st.file_uploader("Upload Image", type=["jpg", "png"])

    if image:
        img = Image.open(image)
        st.image(img, use_column_width=True)

    # CHECK BUTTON
    if st.button("Check Profile"):
        prediction = model.predict([[followers, following, posts, bio_length]])
        prob = model.predict_proba([[followers, following, posts, bio_length]])

        result = "Fake" if prediction[0] == 1 else "Real"
        probability = float(prob[0][1] * 100)

        # SAVE TO DATABASE
        cursor.execute("INSERT INTO history VALUES (?, ?, ?, ?, ?, ?)",
                       (followers, following, posts, bio_length, result, probability))
        conn.commit()

        st.subheader("Result")

        if result == "Fake":
            st.error("⚠️ Fake Profile Detected")
        else:
            st.success("✅ Real Profile")

        st.write(f"Fake Probability: {probability:.2f}%")
        st.progress(int(probability))

        # ---------------- WHY FAKE ----------------
        st.subheader("Why this result?")

        reasons = []

        if followers < 50:
            reasons.append("Very low followers")

        if following > 500:
            reasons.append("Following too many accounts")

        if posts < 5:
            reasons.append("Very few posts")

        if bio_length < 5:
            reasons.append("Bio looks incomplete")

        if reasons:
            for r in reasons:
                st.write(f"- {r}")
        else:
            st.write("Profile looks normal")

    # ---------------- HISTORY ----------------
    st.subheader("Previous Checks")

    cursor.execute("SELECT * FROM history")
    data = cursor.fetchall()

    if data:
        for row in data[::-1]:
            st.write(row)

# ---------------- CONTROL ----------------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if st.session_state["logged_in"]:
    main_app()
else:
    login()