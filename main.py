
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta

#
# App Configuration
#

app = Flask(__name__)
app.secret_key = 'mizuenasekaimiku' # Change this to a random secret key in production

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tastetracker_ps.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

#
# Database Models
#

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.Date, default=date.time.utcnow)

    #User review relationship
    #one user can have mutliple reviews
    # backrerf "author" allows us to access the user from the review
    # lazy = True loads reviews on demand
    reviews = db.relationship('Review', backref='author', lazy=True)


class Review(db.Model):
    review_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    restaurant_name = db.Column(db.String(100), nullable=False)
    cuisine_type = db.Column(db.String(50), nullable=False)
    review_date = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.Date, default=date.time.utcnow)
