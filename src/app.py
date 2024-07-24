import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, People, Favorite
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

#CRUD

@app.route("/people", methods=["GET"])
def get_people():
    people  = People.query.all()
    serialized_people = [person.serialize() for person in people]
    return jsonify({"people": serialized_people}), 201

@app.route("/people/<int:id>", methods=["GET"])
def get_character_by_id(id):
    try:
        person = People.query.get(id)
        if person is None:
            return jsonify({'error': "Character not found!"}), 404
        return jsonify({"person": person.serialize()}), 201
    
    except Exception as error:
        return jsonify({"error": f"{error}"}), 500

@app.route("/planet", methods=["GET"])
def get_planets():
    planets = Planet.query.all()
    serialized_planets = [planet.serialize() for planet in planets]
    return jsonify({"planets": serialized_planets}), 201

@app.route("/planet/<int:id>", methods=["GET"])
def get_planet_by_id(id):
    try:
        planet = Planet.query.get(id)
        if planet is None:
            return jsonify({"error": "Planet not found"}), 404
        return jsonify({"planet": planet.serialize()}), 201

    except Exception as error:
        return jsonify({"error": f"{error}"})

@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    serialized_users = [user.serialize() for user in users]
    return jsonify({"users": serialized_users})

@app.route("/user/<int:user_id>/favorites")
def get_favorites_from_user(user_id):

    if user_id is None:
        return jsonify({"error": "User ID is required"}), 404

    favorites = Favorite.query.filter_by(user_id=user_id).all()
    serialized_favorites = [favorite.serialize() for favorite in favorites]
    return jsonify({"Favorites": serialized_favorites}), 201

@app.route("/favorite/planet/<int:planet_id>/user/<int:user_id>", methods=["POST"])
def add_favorite_planet(planet_id, user_id):

    planet = Planet.query.get(planet_id)

    if planet is None:
        return jsonify({"error": "planet not found"})

    user = User.query.get(user_id)

    if user is None:
        return jsonify({"error": "user not found"})

    existing_favorite = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()

    if existing_favorite is not None:
        return jsonify({"error": "Favorite already exists"}), 409

    favorite = Favorite(planet_id=planet_id, user_id=user_id)

    try:
        db.session.add(favorite)
        db.session.commit()
        db.session.refresh(favorite)

        return jsonify({"message": "Favorite planet added"}), 201

    except Exception as error:
        return jsonify({"error": f"{error}"}), 500

@app.route("/favorite/people/<int:people_id>/user/<int:user_id>", methods=["POST"])
def add_favorite_people(people_id, user_id):

    people = People.query.get(people_id)

    if people is None:
        return jsonify({"error": "person not found"})

    user = User.query.get(user_id)

    if user is None:
        return jsonify({"error": "user not found"})

    existing_favorite = Favorite.query.filter_by(user_id=user_id, people_id=people_id).first()

    if existing_favorite is not None:
        return jsonify({"error": "Favorite already exists"}), 409

    favorite = Favorite(people_id=people_id, user_id=user_id)

    try:
        db.session.add(favorite)
        db.session.commit()
        db.session.refresh(favorite)

        return jsonify({"message": "Favorite person added"})

    except Exception as error:
        return jsonify({"error": f"{error}"}), 500


@app.route("/favorite/planet/<int:planet_id>/user/<int:user_id>", methods=["DELETE"])
def delete_favorite_planet(planet_id, user_id):

    favorite = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()

    if favorite is None:
        return jsonify({"error": "No favorite planet to delete"})

    try:
        db.session.delete(favorite)
        db.session.commit()

        return jsonify({"message": "Favorite planet deleted"})

    except Exception as error:
        return jsonify({"error": f"{error}"}), 500


@app.route("/favorite/people/<int:people_id>/user/<int:user_id>", methods=["DELETE"])
def delete_favorite_user(people_id, user_id):

    favorite = Favorite.query.filter_by(user_id=user_id, people_id=people_id).first()

    if favorite is None:
        return jsonify({"error": "No favorite person to delete"})

    if favorite:
        try:
            db.session.delete(favorite)
            db.session.commit()

            return jsonify({"message": "Favorite person deleted"})

        except Exception as error:
            return jsonify({"error": f"{error}"}), 500
    else:
        return jsonify({"error": "User or favorite not found"}), 404

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
