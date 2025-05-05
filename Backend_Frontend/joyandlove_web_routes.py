from flask import Flask, render_template, jsonify, redirect, url_for, flash, session as flaskSession, request
from sqlalchemy import create_engine, intersect, or_, and_
from sqlalchemy.orm import sessionmaker
from Database.sql_table_joyandlove import Dogs, Raza, character, dog_image
import secrets
import os

joyandlove_web = Flask(__name__)
joyandlove_web.secret_key = os.environ.get("Secret_Key", secrets.token_hex(32))

# Database configuration
DATABASE_URL = "sqlite:///joyandlove_db.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

@joyandlove_web.route('/')
def index():
    return redirect(url_for('home'))

@joyandlove_web.route("/home", methods = ['GET'])
def home():
    """Route for the home page."""
    return render_template("home.html")

@joyandlove_web.route("/foster", methods = ['GET'])
def foster():
    """Route for the home page."""
    return render_template("foster.html")

@joyandlove_web.route("/volunteer", methods = ['GET'])
def volunteer():
    """Route for the home page."""
    return render_template("volunteer.html")

@joyandlove_web.route("/donate", methods = ['GET'])
def donate():
    """Route for the home page."""
    return render_template("donate.html")

@joyandlove_web.route("/adopted_cases", methods=['GET'])
def adopted_cases():
    """Route to display Joy and Love Rescue Alumni (previously adopted dogs)."""

    # Fetch all adopted dogs
    adopted_dogs = session.query(Dogs).filter_by(adopted = True).all()
    
    
    alumni = []

    for dog in adopted_dogs:
        dog_id = dog.dog_id

        behaviors = session.query(character).filter(character.dog_id == dog_id).all()
        typeDog = session.query(Raza).filter(Raza.dog_id == dog_id).all()
        images = session.query(dog_image).filter(dog_image.dog_id == dog_id).all()

        characteristics = [char.characteristic for char in behaviors]
        breeds = [breed.breed for breed in typeDog]
        img_path = [f"{img.img}.jpeg" for img in images]
    
        alumni.append({
            'dog_id': dog.dog_id,
            'name': dog.name,
            'age': dog.age,
            'age_desc': dog.age_desc,
            'sex': dog.sex,
            'breed': ", ".join(breeds),
            'characteristics': ", ".join(characteristics),
            'img': img_path,
            'testimony': dog.story
        })

    flaskSession['adopted_dogs'] = alumni

    return render_template("adopted-cases.html", adopted_dogs = flaskSession['adopted_dogs'])

@joyandlove_web.route("/adopt", methods = ['GET', 'POST'])
def adopt():
    available_dogs = session.query(Dogs).filter_by(adopted = False).all()
    
    """Populating adopt page"""
    breeds = set()
    characteristics = set()
    img_path = set()

    for dog in available_dogs:
        behaviors = session.query(character).filter_by(dog_id = dog.dog_id).all()
        typeDog = session.query(Raza).filter_by(dog_id = dog.dog_id).all()
        imgs = session.query(dog_image).filter_by(dog_id = dog.dog_id).all()
        for race in typeDog:
            breeds.add(race.breed)
        for behavior in behaviors:
            characteristics.add(behavior.characteristic)
        for img in imgs:
            img_path.add(img.img)

    breeds = list(breeds)
    characteristics = list(characteristics)
    img_path = list(img_path)    

    flaskSession['available_dogs'] = [
        {
            'dog_id': dog.dog_id,
            'name': dog.name,
            'age': dog.age,
            'sex': dog.sex,
            'age_desc': dog.age_desc,
        }
        for dog in available_dogs
    ]

    return render_template("adopt.html", available_dogs = flaskSession['available_dogs'], breeds = breeds, characteristics = characteristics, image = img_path)

@joyandlove_web.route('/filter_dogs', methods=['POST'])
def filter_dogs():
    name = request.json.get('name', '')
    sex = request.json.get('sex', [])
    breed = request.json.get('breed', [])
    characteristics = request.json.get('characteristics', [])
    age = request.json.get('age', [])
    age = [int(value) for value in age]

    query = session.query(Dogs).filter_by(adopted = False)

    if name:
        query = query.filter(Dogs.name.ilike(f'%{name}%'))
    if sex:
        query = query.filter(Dogs.sex.in_(sex))
    if breed:
        query = query.join(Raza).filter(Raza.breed.in_(breed))
    if characteristics:
        query = query.join(character).filter(character.characteristic.in_(characteristics))
    if age:
        age_filters = []
        if 1 in age:
            age_filters.append(or_(Dogs.age_desc == "month", and_(Dogs.age < 2, Dogs.age_desc == "year")))
        if 7 in age:
            age_filters.append(and_(Dogs.age > 1, Dogs.age_desc == "year", Dogs.age < 8))
        if 8 in age:
            age_filters.append(and_(Dogs.age > 7, Dogs.age_desc == "year"))
        query = query.filter(or_(*age_filters))
    
    dogs = query.all()

    # Convert the query results to a list of dictionaries
    dog_list = [{
        'dog_id': dog.dog_id,
        'name': dog.name,
        'age': dog.age,
        'sex': dog.sex,
        'age_desc': dog.age_desc,
    } for dog in dogs]

    return jsonify(dog_list)

@joyandlove_web.route("/dog_details/<int:dog_id>", methods=["GET"])
def dog_details(dog_id):
    """Route for the dog details page."""
    dog = session.query(Dogs).filter_by(dog_id = dog_id).first()
    if not dog:
        return jsonify({'error': 'Dog not found'}), 404
    
    behaviors = session.query(character).filter(character.dog_id == dog_id).all()
    typeDog = session.query(Raza).filter(Raza.dog_id == dog_id).all()
    images = session.query(dog_image).filter(dog_image.dog_id == dog_id).all()

    characteristics = [char.characteristic for char in behaviors]
    breeds = [breed.breed for breed in typeDog]
    img_path = [f"{img.img}.jpeg" for img in images]

    flaskSession['dog_details'] = {
        'dog_id': dog_id,
        'name': dog.name,
        'age': dog.age,
        'sex': dog.sex,
        'age_desc': dog.age_desc,
        'breed': ", ".join(breeds),
        'behaviors': ", ".join(characteristics),
        'img': img_path,
        'story': dog.story,
        'fee': dog.fee
    }
    
    return redirect(url_for('adopt'))

@joyandlove_web.route('/clear_dog_session', methods=['GET'])
def clear_dog_session():
    flaskSession.pop('dog_details', None)
    return '', 204

if __name__ == "__main__":
    joyandlove_web.run(debug=True)