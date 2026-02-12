from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta, datetime

#
# App Configuration
#

app = Flask(__name__)
app.secret_key = 'secretkeyandstuff' # Change this to a random secret key in production

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tastetracker_rm.db'
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
    created_at = db.Column(db.Date, default=datetime.utcnow)

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
    review_date = db.Column(db.Date, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.Date, default=datetime.utcnow)

@app.context_processor
def inject_user():
    return dict(logged_in=("user_id" in session))

@app.route("/add", methods=["GET", "POST"])
def add_review():
    # Block access if not logged in
    if "user_id" not in session:
        flash("You must be logged in to add a review.")
        return redirect(url_for("login"))

    if request.method == "POST":
        restaurant_name = request.form.get("restaurant_name")
        cuisine_type = request.form.get("cuisine_type")
        rating = request.form.get("rating")
        review_text = request.form.get("review_text")

        new_review = Review(
            user_id=session["user_id"],
            restaurant_name=restaurant_name,
            cuisine_type=cuisine_type,
            review_date=datetime.utcnow(),  # simple example
            rating=int(rating),
            review_text=review_text
        )

        db.session.add(new_review)
        db.session.commit()

        flash("Review added successfully!")
        return redirect(url_for("home"))

    return render_template("add_review.html")


#Home Route - View All Reviews

@app.route("/")
def home():
    reviews = Review.query.order_by(Review.created_at.desc()).all() # Fetch all reviews, newest first
    return render_template("home.html", reviews=reviews) # Render home template with reviews

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Simple username from email (before @)
        username = email.split("@")[0]

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered.")
            return redirect(url_for("register"))

        # Hash password
        hashed_password = generate_password_hash(password)

        # Create new user
        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_password
        )

        # Add to database
        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully!")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            session["user_id"] = user.user_id
            flash("Logged in successfully!")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password.")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.")
    return redirect(url_for("home"))




@app.route("/dashboard")
def dashboard():
    reviews = User.query.all()
    return render_template("dashboard.html", reviews=reviews) # Render register template



#run app, keep at bottom

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)