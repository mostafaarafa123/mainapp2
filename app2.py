import streamlit as st  # Import Streamlit for creating the web interface
import sqlite3  # Import SQLite for database operations
import pandas as pd  # Import Pandas for data manipulation

# Function to initialize the database
def init_db():
    conn = sqlite3.connect("medical.db")  # Connect to the SQLite database
    cursor = conn.cursor()  # Create a cursor object to interact with the database
    # Create a users table if it doesn't exist
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, password TEXT)")
    # Create a doctors table if it doesn't exist
    cursor.execute("CREATE TABLE IF NOT EXISTS doctors (id INTEGER PRIMARY KEY, name TEXT, specialty TEXT, rating REAL, image_url TEXT)")
    conn.commit()  # Commit the changes to the database
    conn.close()  # Close the database connection

# Function to register a new user
def register(email, password):
    conn = sqlite3.connect("medical.db")  # Connect to the database
    cursor = conn.cursor()  # Create a cursor object
    try:
        # Insert a new user into the users table
        cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        conn.commit()  # Commit the changes
        return True  # Return True if registration is successful
    except sqlite3.IntegrityError:
        return False  # Return False if the email already exists
    finally:
        conn.close()  # Close the database connection

# Function to log in a user
def login(email, password):
    conn = sqlite3.connect("medical.db")  # Connect to the database
    cursor = conn.cursor()  # Create a cursor object
    cursor.execute("SELECT password FROM users WHERE email = ?", (email,))  # Fetch the password for the given email
    user = cursor.fetchone()  # Retrieve the user data
    conn.close()  # Close the database connection
    return user and user[0] == password  # Check if the password matches

# Function to load doctors from the database
def load_doctors():
    try:
        conn = sqlite3.connect("medical.db")  # Connect to the database
        df = pd.read_sql("SELECT * FROM doctors", conn)  # Read doctor data into a Pandas DataFrame
        return df  # Return the DataFrame
    except Exception as e:
        st.error(f"Error loading doctors: {e}")  # Display an error message if an exception occurs
        return pd.DataFrame()  # Return an empty DataFrame in case of error
    finally:
        conn.close()  # Close the database connection

# Function to add a new doctor
def add_doctor(name, specialty, rating, image_url):
    if not name or not specialty or not image_url:  # Check if all fields are filled
        st.error("All fields are required!")  # Display an error message if fields are empty
        return
    
    conn = sqlite3.connect("medical.db")  # Connect to the database
    cursor = conn.cursor()  # Create a cursor object
    # Insert a new doctor into the doctors table
    cursor.execute("INSERT INTO doctors (name, specialty, rating, image_url) VALUES (?, ?, ?, ?)", (name, specialty, rating, image_url))
    conn.commit()  # Commit the changes
    conn.close()  # Close the database connection
    st.success("Doctor added successfully!")  # Display a success message

# Function to display the list of doctors
def show_doctors():
    doctors = load_doctors()  # Load the doctors from the database
    for _, row in doctors.iterrows():  # Iterate through each doctor
        with st.container():  # Create a new container for each doctor
            st.image(row['image_url'], width=120)  # Display the doctor's image
            st.write(f"**{row['name']}** - *{row['specialty']}* - ⭐ {row['rating']}")  # Display doctor's information
            with st.form(key=f"book_form_{row['id']}"):  # Create a form for booking an appointment
                submit = st.form_submit_button(f"Book Appointment with {row['name']}")  # Button to confirm booking
                if submit:
                    # Store selected doctor's information for booking
                    st.session_state.selected_doctor = row['name']
                    st.session_state.page = "Book Appointment"  # Navigate to the booking page

# Function for the home page
def home():
    st.title("🏥 Medical Appointment Booking")  # Title of the page
    if st.button("➕ Add Doctor"):  # Button to add a new doctor
        name = st.text_input("Doctor's Name")  # Input field for doctor's name
        specialty = st.text_input("Specialty")  # Input field for specialty
        rating = st.slider("Rating", 1.0, 5.0, 4.5)  # Slider for rating
        image_url = st.text_input("Doctor's Image URL")  # Input field for image URL
        if st.button("Add"):  # Button to add the doctor
            add_doctor(name, specialty, rating, image_url)  # Call the function to add the doctor
    
    show_doctors()  # Display the list of doctors

# Function for the booking interface
def booking():
    st.title("📅 Book an Appointment")  # Title of the booking page
    if 'selected_doctor' in st.session_state:  # Check if a doctor has been selected
        st.subheader(f"Book an appointment with **{st.session_state.selected_doctor}**")  # Display selected doctor's name
        date = st.date_input("📆 Select Date")  # Input field for selecting date
        time = st.time_input("⏰ Select Time")  # Input field for selecting time
        
        if st.button("Confirm Booking"):  # Button to confirm the booking
            st.success(f"✅ Appointment booked successfully with **{st.session_state.selected_doctor}** on {date} at {time}.")  # Display success message
        if st.button("🔙 Back to Home"):  # Button to go back to the home page
            st.session_state.page = "Home"  # Change the page to home
            st.rerun()  # Rerun the app
    else:
        st.warning("Please select a doctor first.")  # Warning if no doctor is selected

# Function for the login and registration interface
def show_auth():
    st.title("🔑 Login or Register")  # Title of the authentication page
    choice = st.radio("Select an option", ["Login", "Register"])  # Options for login or registration
    
    email = st.text_input("Email", key="auth_email")  # Input field for email
    password = st.text_input("Password", type="password", key="auth_password")  # Input field for password
    
    if choice == "Login":  # If login is selected
        if st.button("Login"):  # Button to log in
            if login(email, password):  # Check login credentials
                st.session_state.page = "Home"  # Navigate to the home page
                st.success("Login successful!")  # Display success message
                st.rerun()  # Rerun the app
            else:
                st.error("Invalid email or password")  # Display error message
    else:  # If registration is selected
        if st.button("Register"):  # Button to register
            if register(email, password):  # Attempt to register the user
                st.success("Registration successful! You can now log in.")  # Display success message
            else:
                st.error("Email already exists. Try a different one.")  # Display error message

# Initialize the database on startup
init_db()  # Call the function to initialize the database

# Manage page navigation
if "page" not in st.session_state:  # Check if the page state exists
    st.session_state.page = "Auth"  # Set the default page
    # Determine the current page based on the session state
if st.session_state.page == "Home":
    home()  # Call the home function to display the home page
elif st.session_state.page == "Book Appointment":
    booking()  # Call the booking function to display the booking page
elif st.session_state.page == "Auth":
    show_auth()  # Call the authentication function to display the login/register page