from app import app
print("URI:", app.config['SQLALCHEMY_DATABASE_URI'])
print("CWD:", __import__('os').getcwd())