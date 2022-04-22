import flask
import os

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


from flask_sqlalchemy import SQLAlchemy

app = flask.Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = os.getenv("secret_key")
db = SQLAlchemy(app)
