import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from db import init_db

def handler(*args):
    init_db()
    return {"status": "Database initialized"}
