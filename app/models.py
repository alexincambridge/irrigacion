import sqlite3
import os
from flask import g
from flask_login import UserMixin

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "instance", "irrigacion.db")

class User(UserMixin):
    def __init__(self, id, username):
        self.id = str(id)
        self.username = username

# def get_db():
#     if "db" not in g:
#         g.db = sqlite3.connect(DB_PATH)
#         g.db.row_factory = sqlite3.Row
#     return g.db

# app/models.py
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect("instance/irrigacion.db")
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()
