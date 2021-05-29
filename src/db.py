#!/usr/bin/env python

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Game(db.Model):
    __tablename__ = "games"

    id     = db.Column(db.Integer, primary_key=True)
    name   = db.Column(db.String(128), unique=True, nullable=False)
    rating = db.Column(db.Integer, default=-1, nullable=False)

    def __init__(self,name,rating):
        self.name    = name
        self.rating  = rating
