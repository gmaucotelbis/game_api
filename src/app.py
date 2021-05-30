#!/usr/bin/env python

import datetime
from flask import Flask, jsonify, abort, request
import traceback
import sys

from src.db import db, Game, Platform

app = Flask(__name__)
app.config.from_object("src.config.Config")
db.init_app(app)

@app.route("/get/<id>")
def get(id):
    try:
        id = int(id)
    except BaseException:
        abort(400,"Invalid data")
    game = Game.query.filter_by(id=id).first()
    if(game is None):
        abort(404,'Unknown game')
    return jsonify(name=game.name,rating=game.rating)

@app.route("/set", methods=['POST'])
def set():
    try:
        request.get_json(force=True)
        name     = request.json["name"]
        # checking the game is not registered
        if(Game.query.filter(Game.name.ilike(name)) is not None):
            abort(400,"Game already is database")
        ratings  = request.json["ratings"]
        studio   = request.json["studio"]
        release_date = datetime.date.fromstring(request.json["release_date"])
        game     = Game(name, ratings, studio)
        for platform in request.json["platforms"]:
            existing_platform = Platform.query.filter(Platform.name.ilike(platform)).one_or_none()
            if(existing_platform is None):
                game.platforms.append(Platform(platform))
            else:
                game.platforms.append(existing_platform)
        db.session.add(game)
        db.session.commit()
    except BaseException:
        print(f"{traceback.format_exc()}\n{sys.exc_info()[0]}")
        abort(400,'Invalid data')
    return "saved"
