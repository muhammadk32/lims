from app import app
from extensions import db
import os

uri = app.config['SQLALCHEMY_DATABASE_URI']
print("URI:", uri)
print("instance_path:", app.instance_path)

# Resolve the actual file path
if uri.startswith("sqlite:///"):
    path = uri.replace("sqlite:///", "", 1)
    if not os.path.isabs(path):
        # Flask-SQLAlchemy resolves relative paths against instance_path
        path = os.path.join(app.instance_path, path)
    print("Resolved DB file:", os.path.abspath(path))
    print("Exists:", os.path.exists(path))
    if os.path.exists(path):
        print("Size (bytes):", os.path.getsize(path))