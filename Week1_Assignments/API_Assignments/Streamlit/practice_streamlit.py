import streamlit as st

st.title("Entry Validation")

name = st.text_input("Enter your name")

if st.button("Check") :
    if name :
        st.success(f"Hello {name}, welcome to the communty")
    else :
        st.warning("Pls, enter your name")