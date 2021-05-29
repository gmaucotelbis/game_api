#!/usr/bin/env python

from flask import Flask, jsonify, abort, request
import traceback
import sys

from src.db import db, Game

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
        print(request.get_json(force=True))
        name = request.json["name"]
        rating = request.json["rating"]
        game = Game(name,rating)
        db.session.add(game)
        db.session.commit()
    except BaseException:
        print(f"{traceback.format_exc()}\n{sys.exc_info()[0]}")
        abort(400,'Invalid data')
    return "saved"
