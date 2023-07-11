from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)

""" 
    Relationships
        Planet has_many Missions
        Scientist has_many Missions
        Mission belongs_to Planet
        Mission belongs_to Scientist

        Planet has_many Scientists through Missions
        Scientist has_many Planets through Missions
        Planet many_to_many Scientists
"""


class Planet(db.Model, SerializerMixin):
    __tablename__ = 'planets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    distance_from_earth = db.Column(db.Integer)
    nearest_star = db.Column(db.String)

    # Add relationship
    missions = db.relationship(
        "Mission", backref="planet", cascade="all, delete-orphan")

    # Add serialization rules
    serialize_rules = ("-missions.planet",)


class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    field_of_study = db.Column(db.String)

    # Add relationship
    missions = db.relationship(
        "Mission", backref="scientist", cascade="all, delete-orphan")

    # Add serialization rules
    serialize_rules = ("-missions.scientist",)

    # Add validation
    # @validates("name")
    # def validate_name(self, key, name):
    #     if isinstance(name, str) and len(name) > 0:
    #         return name
    #     raise ValueError("Name must be a non empty String")

    # @validates("field_of_study")
    # def validate_field_of_study(self, key, field_of_study):
    #     if value and len(field_of_study) > 0:
    #         return field_of_study
    #     raise ValueError("Field of Study must be a non empty String")

    @validates("field_of_study", "name")
    def validate_value(self, key, value):
        # if value and len(value) > 0:
        if isinstance(value, str) and len(value) > 0:
            return value
        raise ValueError(f"{key} must be a non empty String")


class Mission(db.Model, SerializerMixin):
    __tablename__ = 'missions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    # Add relationships
    scientist_id = db.Column(db.Integer, db.ForeignKey(
        "scientists.id"), nullable=False)
    planet_id = db.Column(db.Integer, db.ForeignKey(
        "planets.id"), nullable=False)

    # In backref
    # also creates a method called "scientist" that finds the scientist related
    # Add serialization rules
    serialize_rules = ("-scientist.missions", "-planet.missions")

    # Add validation
    @validates("name")
    def validate_name(self, key, value):
        if isinstance(value, str) and len(value) > 0:
            return value
        raise ValueError("Name must be a non empty String")

    @validates("scientist_id", "planet_id")
    def validate_value(self, key, value):
        print("***************************")
        print(f'{key} : {value}')
        if isinstance(value, int):
            return value
        raise ValueError(f"Mission must have a {key}")


# add any models you may need.
