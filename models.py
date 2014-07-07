from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    prep_time = db.Column(db.String(100))
    cook_time = db.Column(db.String(100))
    ingredients = db.Column(db.Text)
    instructions = db.Column(db.Text)
    rating = db.Column(db.Integer)
