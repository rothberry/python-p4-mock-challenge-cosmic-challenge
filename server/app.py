#!/usr/bin/env python3
from ipdb import set_trace
from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route('/')
def home():
    return ''


class Scientists(Resource):
    # Index
    def get(self):
        all_scientists = [scientist.to_dict(
            only=("id", "name", "field_of_study")) for scientist in Scientist.query.all()]
        return make_response(all_scientists)

    # Create
    def post(self):
        form_json = request.get_json()
        try:
            new_scientist = Scientist(
                name=form_json["name"], field_of_study=form_json["field_of_study"])
            db.session.add(new_scientist)
            db.session.commit()
            return make_response(new_scientist.to_dict(rules=("-missions",)), 201)
        except ValueError as err:
            return make_response({"errors": str(err)}, 422)


class ScientistById(Resource):
    # Show
    def get(self, sci_id):
        found_scientist = Scientist.query.filter_by(id=sci_id).first()
        if not found_scientist:
            return make_response({"error": "Scientist not found"}, 404)
        return make_response(found_scientist.to_dict())

    # Update
    def patch(self, sci_id):
        found_scientist = Scientist.query.filter_by(id=sci_id).first()
        if not found_scientist:
            return make_response({"error": "Scientist not found"}, 404)

        form_json = request.get_json()
        try:
            for key in form_json:
                setattr(found_scientist, key, form_json[key])

            db.session.add(found_scientist)
            db.session.commit()

            return make_response(found_scientist.to_dict(rules=("-missions",)), 202)

        except ValueError as err:
            return make_response({"errors": str(err)}, 422)

    # Delete
    def delete(self, sci_id):
        found_scientist = Scientist.query.filter_by(id=sci_id).first()
        if not found_scientist:
            return make_response({"error": "Scientist not found"}, 404)

        db.session.delete(found_scientist)
        db.session.commit()
        return make_response({}, 204)


class Planets(Resource):
    # Index
    def get(self):
        all_planets = [planet.to_dict(
            rules=("-missions", "-scientists")) for planet in Planet.query.all()]
        return make_response(all_planets)


class Missions(Resource):
    # Create
    def post(self):
        form_json = request.get_json()
        try:
            new_mission = Mission(
                name=form_json["name"],
                scientist_id=form_json["scientist_id"],
                planet_id=form_json["planet_id"],
            )
            db.session.add(new_mission)
            db.session.commit()
            return make_response(new_mission.to_dict(), 201)
        except ValueError as err:
            return make_response({"errors": str(err)}, 422)


api.add_resource(Scientists, "/scientists")
api.add_resource(ScientistById, "/scientists/<int:sci_id>")
api.add_resource(Planets, "/planets")
api.add_resource(Missions, "/missions")

if __name__ == '__main__':
    app.run(port=5555, debug=True)
