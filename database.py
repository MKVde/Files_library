import os

from deta import Deta  # pip install deta
from dotenv import load_dotenv  # pip install python-dotenv


# Load the environment variables
load_dotenv(".env")
DETA_KEY = os.getenv("DETA_KEY")

deta = Deta(DETA_KEY)

dba = deta.Base("UserNames")

def insert_user(username, name, password):
    """Returns the user on a successful user creation, otherwise raises and error"""
    return dba.put({"key": username, "name": name, "password": password})

def fetch_all_users():
    """Returns a dict of all users"""
    res = dba.fetch()
    return res.items

def get_user(username):
    """If not found, the function will return None"""
    return dba.get(username)


def update_user(username, updates):
    """If the item is updated, returns None. Otherwise, an exception is raised"""
    return dba.update(updates, username)


def delete_user(username):
    """Always returns None, even if the key does not exist"""
    return dba.delete(username)
