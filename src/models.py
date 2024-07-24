import os
import sys
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Enum as SqlEnum
from sqlalchemy.orm import relationship, declarative_base
from enum import Enum as PyEnum

db = SQLAlchemy()

class UserRole(PyEnum):
    ADMIN = 'admin'
    USER = 'user'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    is_banned = db.Column(Boolean, default=False)
    role = db.Column(SqlEnum(UserRole), nullable=False)
    favorite = db.relationship("Favorite", backref="favorite", lazy=True)

    def serialize(self):
        return{
            "id": self.id,
            "email": self.email
        }

    def __repr__(self):
        return f"<User: {self.email}>"

class People(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(1000), nullable=False)

    def serialize(self):
        return{
            "id": self.id,
            "name": self.name,
            "description": self.description
        }

    def __repr__(self):
        return f"<Person: {self.name}>"

class Planet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(1000), nullable=False)

    def serialize(self):
        return{
            "id": self.id,
            "name": self.name,
            "description": self.description
        }

    def __repr__(self):
        return f"<Planet: {self.name}>"

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    people_id = db.Column(db.Integer, db.ForeignKey('people.id'))
    planet_id = db.Column(db.Integer, db.ForeignKey('planet.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    people = db.relationship(People)
    planet = db.relationship(Planet)
    user = db.relationship(User)

    def serialize(self):
        return {
            "id": self.id,
            "people id": self.people_id,
            "planet id": self.planet_id,
            "user_id": self.user_id
        }



