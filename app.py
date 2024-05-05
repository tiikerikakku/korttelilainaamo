from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import getenv

app = Flask(__name__)

app.secret_key = getenv('SECRET')

app.config['SQLALCHEMY_DATABASE_URI'] = getenv('DATABASE')
db = SQLAlchemy(app)

# pylint: disable=unused-import

import routes
