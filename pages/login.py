import streamlit as st
import streamlit_extras
from streamlit_extras.switch_page_button import switch_page
import sqlite3

conn = sqlite3.connect('users.db',check_same_thread=False)
cursor = conn.cursor()

st.set_page_config(initial_sidebar_state='collapsed')

st.title('LOGIN PAGE')

# get the username and password from the user
st.write('Login with your credentials')
with st.form(key='Login Form'):
    username = st.text_input("Enter your username: ")
    password = st.text_input("Enter your password: ")
    submit = st.form_submit_button('Login')
    
    if submit:
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username,password))
        
        
        # get the result (if its valid or not)
        result = cursor.fetchone()
        
        
        # check if its valid
        if result:
            # storing the username
            st.session_state['username'] = username
            
            st.success('Login Successful!')
            switch_page('main')
        else:
            st.error('Invalid username or password')

# send the username and password to the main file