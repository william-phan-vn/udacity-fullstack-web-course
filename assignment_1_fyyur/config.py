import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True
SQLALCHEMY_TRACK_MODIFICATIONS = False

# To see the SQL queries being printed on the terminal
SQLALCHEMY_ECHO = True

# Connect to the database


# DONE IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://vietplh1:123@localhost:5432/udacity-asm1-fyyur'
