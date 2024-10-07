import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import sqlite3

st.set_page_config(initial_sidebar_state='collapsed')

conn = sqlite3.connect('users.db',check_same_thread=False)
cursor = conn.cursor()

st.title('SIGN IN PAGE')

# get user to set up their username and password
st.write("Enter Your information")
with st.form(key='Registration Form'):
    username = st.text_input('Enter your name: ')
    password = st.text_input('Choose a password')
    submit = st.form_submit_button('Add User')
    
    if submit:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (USERNAME TEXT(50), PASSWORD TEXT(50))
            """
        )
        cursor.execute("INSERT INTO users VALUES (?,?)", (username,password))

        conn.commit()
        conn.close()
        
        # now go to login page
        switch_page('login')
        
if st.button('Already a user? Sign in'):
    switch_page('login')

