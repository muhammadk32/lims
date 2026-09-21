from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# Create instances WITHOUT binding to an app yet.
# They'll be attached inside create_app() in app.py.

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

# Where to redirect when a login is required
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'