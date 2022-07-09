from .server import *


def sign_up_user(username, encrypted_password, nonce, tag, password_signature, encrypted_session_key, user_pub_key):
    successful, err = sign_up(username, encrypted_password, nonce, tag, password_signature, encrypted_session_key, user_pub_key)
    if successful:
        return "User signed up successfully", None
    else:
        return "An error occurred during signing up user", err

def user_command(username, encrypted_command, nonce, tag):
    response, err = exec_user_command(username, encrypted_command, nonce, tag)
    return response, err
