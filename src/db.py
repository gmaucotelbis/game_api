#!/usr/bin/env python

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

game_platform = db.Table('game_platform',
            db.Column('game_id', db.Integer, db.ForeignKey('games.id'), primary_key=True),
            db.Column('platform_id', db.Integer, db.ForeignKey('platforms.id'), primary_key=True)
            )
            

class Game(db.Model):
    __tablename__ = "games"

    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(128), unique=True, nullable=False)
    studio       = db.Column(db.String(128), unique=False, nullable=False)
    ratings      = db.Column(db.Integer, nullable=False)
    release_date = db.Column(db.Date, nullable=False) 
    platforms = db.relationship('Platform', secondary=game_platform, lazy='subquery', backref=db.backref('games', lazy=True))

    def __init__(self, name, ratings, studio, release_date):
        self.name         = name
        self.ratings      = ratings
        self.studio       = studio
        self.release_date = release_date

class Platform(db.Model):
    __tablename__ = "platforms"

    id    = db.Column(db.Integer, primary_key=True)
    name  = db.Column(db.String(128), unique=True, nullable=False)

    def __init__(self,name):
        self.name = name
