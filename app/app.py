from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Configuratie voor de database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///burgerapp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Modellen

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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

# Basisroutes voor de API

@app.route('/')
def home():
    return "Welkom bij de Burger App API!"

@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    new_user = User(username=data['username'], email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created successfully!"}), 201

@app.route('/chains', methods=['POST'])
def create_chain():
    data = request.json
    new_chain = Chain(name=data['name'], location=data.get('location'))
    db.session.add(new_chain)
    db.session.commit()
    return jsonify({"message": "Chain added successfully!"}), 201

@app.route('/chains', methods=['GET'])
def get_chains():
    chains = Chain.query.all()
    response = [
        {
            "id": chain.id,
            "name": chain.name,
            "location": chain.location
        } for chain in chains
    ]
    return jsonify(response)

@app.route('/burgers', methods=['POST'])
def create_burger():
    data = request.json
    new_burger = Burger(name=data['name'], chain_id=data['chain_id'], description=data.get('description'))
    db.session.add(new_burger)
    db.session.commit()
    return jsonify({"message": "Burger added successfully!"}), 201

@app.route('/reviews', methods=['POST'])
def create_review():
    data = request.json
    new_review = Review(
        user_id=data['user_id'],
        burger_id=data['burger_id'],
        rating=data['rating'],
        comment=data.get('comment'),
        photo_url=data.get('photo_url')
    )
    db.session.add(new_review)
    db.session.commit()
    return jsonify({"message": "Review added successfully!"}), 201

@app.route('/reviews/<int:burger_id>', methods=['GET'])
def get_reviews(burger_id):
    reviews = Review.query.filter_by(burger_id=burger_id).all()
    response = [
        {
            "id": review.id,
            "user_id": review.user_id,
            "rating": review.rating,
            "comment": review.comment,
            "photo_url": review.photo_url,
            "created_at": review.created_at
        } for review in reviews
    ]
    return jsonify(response)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Zorgt ervoor dat de database wordt aangemaakt
    app.run(debug=True)

