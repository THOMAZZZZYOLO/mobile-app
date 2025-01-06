from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Voor sessiebeveiliging
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///burgerapp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # De route die ge-wacht wordt voor inloggen

# Database-modellen

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Chain(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    location = db.Column(db.String(200), nullable=True)

class Burger(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    chain_id = db.Column(db.Integer, db.ForeignKey('chain.id'), nullable=False)
    description = db.Column(db.Text, nullable=True)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    burger_id = db.Column(db.Integer, db.ForeignKey('burger.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    photo_url = db.Column(db.String(250), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes voor de app

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully!')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route('/chains', methods=['GET'])
def get_chains():
    chains = Chain.query.all()
    return render_template('chains.html', chains=chains)

@app.route('/burgers')
def burgers():
    burgers = Burger.query.all()
    return render_template('burgers.html', burgers=burgers)

@app.route('/burgers/<int:burger_id>/reviews')
def burger_reviews(burger_id):
    burger = Burger.query.get(burger_id)
    reviews = Review.query.filter_by(burger_id=burger_id).all()
    return render_template('burger_reviews.html', burger=burger, reviews=reviews)

@app.route('/reviews', methods=['POST'])
@login_required
def create_review():
    data = request.form
    burger_id = data['burger_id']
    rating = data['rating']
    comment = data['comment']
    photo_url = data.get('photo_url')

    new_review = Review(
        user_id=current_user.id,
        burger_id=burger_id,
        rating=rating,
        comment=comment,
        photo_url=photo_url
    )
    db.session.add(new_review)
    db.session.commit()
    return redirect(url_for('burger_reviews', burger_id=burger_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Zorgt ervoor dat de database wordt aangemaakt
    app.run(debug=True)