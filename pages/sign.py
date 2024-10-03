import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import sqlite3

conn = sqlite3.connect('users.db',check_same_thread=False)
cursor = conn.cursor()


# get user to set up their username and password
st.write("Please fill out this form")
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
        st.success('User has been added')
        
        # now go to login page
        switch_page('login')

