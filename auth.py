"""
auth.py
--------
Module 1: User Management.
Just register and login. Kept simple on purpose.
"""

from database import add_user, get_user


def register_user(username, password):
    """
    Tries to create a new account.
    Returns (success, message).
    """
    # Basic validation - no empty or too-short stuff
    if not username or not password:
        return False, "Please fill in both fields."

    if len(username) < 3:
        return False, "Username must be at least 3 characters."

    if len(password) < 4:
        return False, "Password must be at least 4 characters."

    if add_user(username, password, role="staff"):
        return True, "Account created! You can log in now."
    else:
        return False, "That username is already taken."


def login_user(username, password):
    """
    Checks credentials.
    Returns (user_row_or_None, message).
    """
    if not username or not password:
        return None, "Please fill in both fields."

    user = get_user(username, password)
    if user:
        return user, "Welcome back!"
    else:
        return None, "Wrong username or password."