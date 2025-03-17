import streamlit as st  # Import Streamlit for creating the web interface
import sqlite3  # Import SQLite for database operations
import pandas as pd  # Import Pandas for data manipulation

# Function to initialize the database
def init_db():
    conn = sqlite3.connect("medical.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, password TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS doctors (id INTEGER PRIMARY KEY, name TEXT, specialty TEXT, rating REAL, image_url TEXT)")
    conn.commit()
    conn.close()

# Function to register a new user
def register(email, password):
    conn = sqlite3.connect("medical.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# Function to log in a user
def login(email, password):
    conn = sqlite3.connect("medical.db")
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user and user[0] == password

# Function to load doctors from the database
def load_doctors():
    conn = sqlite3.connect("medical.db")
    df = pd.read_sql("SELECT * FROM doctors", conn)
    conn.close()
    return df

# Function to add a new doctor
def add_doctor(name, specialty, rating, image_url):
    if not name or not specialty or not image_url:
        st.error("All fields are required!")
        return
    conn = sqlite3.connect("medical.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO doctors (name, specialty, rating, image_url) VALUES (?, ?, ?, ?)", (name, specialty, rating, image_url))
    conn.commit()
    conn.close()
    st.success("Doctor added successfully!")
    st.rerun()

# Function to display the list of doctors
def show_doctors():
    doctors = load_doctors()
    for _, row in doctors.iterrows():
        with st.container():
            st.image(row['image_url'], width=120)
            st.write(f"**{row['name']}** - *{row['specialty']}* - ⭐ {row['rating']}")
            if st.button(f"Book Appointment with {row['name']}", key=f"book_{row['id']}"):
                st.session_state.selected_doctor = row['name']
                st.session_state.page = "Book Appointment"
                st.rerun()

# Function for the home page
def home():
    st.title("🏥 Medical Appointment Booking")
    if st.button("➕ Add Doctor"):
        st.session_state.page = "Add Doctor"
        st.rerun()
    show_doctors()

# Function for the booking interface
def booking():
    st.title("📅 Book an Appointment")
    if 'selected_doctor' in st.session_state:
        st.subheader(f"Book an appointment with **{st.session_state.selected_doctor}**")
        date = st.date_input("📆 Select Date")
        time = st.time_input("⏰ Select Time")
        if st.button("Confirm Booking"):
            st.success(f"✅ Appointment booked successfully with **{st.session_state.selected_doctor}** on {date} at {time}.")
        if st.button("🔙 Back to Home"):
            st.session_state.page = "Home"
            st.rerun()
    else:
        st.warning("Please select a doctor first.")

# Function to add a doctor page
def add_doctor_page():
    st.title("➕ Add a New Doctor")
    name = st.text_input("Doctor's Name")
    specialty = st.text_input("Specialty")
    rating = st.slider("Rating", 1.0, 5.0, 4.5)
    image_url = st.text_input("Doctor's Image URL")
    if st.button("Add"):
        add_doctor(name, specialty, rating, image_url)
    if st.button("🔙 Back to Home"):
        st.session_state.page = "Home"
        st.rerun()

# Function for the login and registration interface
def show_auth():
    st.title("🔑 Login or Register")
    choice = st.radio("Select an option", ["Login", "Register"])
    email = st.text_input("Email", key="auth_email")
    password = st.text_input("Password", type="password", key="auth_password")
    if choice == "Login":
        if st.button("Login"):
            if login(email, password):
                st.session_state.page = "Home"
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid email or password")
    else:
        if st.button("Register"):
            if register(email, password):
                st.success("Registration successful! You can now log in.")
            else:
                st.error("Email already exists. Try a different one.")

# Initialize the database on startup
init_db()

# Manage page navigation
if "page" not in st.session_state:
    st.session_state.page = "Auth"

if st.session_state.page == "Home":
    home()
elif st.session_state.page == "Book Appointment":
    booking()
elif st.session_state.page == "Auth":
    show_auth()
elif st.session_state.page == "Add Doctor":
    add_doctor_page()
