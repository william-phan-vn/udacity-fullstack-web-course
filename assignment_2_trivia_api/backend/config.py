import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True
SQLALCHEMY_TRACK_MODIFICATIONS = False

# To see the SQL queries being printed on the terminal
SQLALCHEMY_ECHO = False

# IMPLEMENT DATABASE URL
database_name = 'trivia'
SQLALCHEMY_DATABASE_URI = 'postgres://{}/{}'.format('localhost:5432', database_name)
