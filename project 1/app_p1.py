import streamlit as st

st.title("Project 1: The 'Hello World' Web UI")
st.header("this web-app will greet the user based on their input.")
name = st.text_input("Enter your name :")
submit_name = st.button("Submit Name." ,type="primary")
if submit_name:
    if( name=="") or (name==None):
        st.warning("empty input please enter a name.")
    else:

        st.success(f"Hello {name}, nice to see you !Welcome to building AI apps." )

