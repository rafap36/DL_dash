import streamlit_authenticator as stauth

hashed_passwords = stauth.Hasher(['mrsk@23']).generate()

print(hashed_passwords)
