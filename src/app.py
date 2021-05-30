#!/usr/bin/env python

import datetime
from flask import Flask, jsonify, abort, request
import traceback
import sys

from src.db import db, Game, Platform, Studio

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
    return jsonify(
                name=game.name,
                ratings=game.ratings,
                studio=game.studio.name,
                realease_date=game.release_date.isoformat(),
                platforms=[ platform.name for platform in game.platforms ]
                )

@app.route("/set", methods=['POST'])
def set():
    try:
        request.get_json(force=True)
        name     = request.json["name"]
        # checking the game is not registered
        if Game.query.filter(Game.name.ilike(name)).one_or_none() is not None :
            abort(400,"Game already is database")
        ratings  = int(request.json["ratings"])
        studio   = request.json["studio"]
        release_date = datetime.datetime.strptime(request.json["release_date"], "%Y-%m-%d").date()
        game     = Game(name, ratings, release_date)
        existing_studio = Studio.query.filter(Studio.name.ilike(studio)).one_or_none()
        if existing_studio is None:
            game.studio = Studio(studio)
        else:
            game.studio = existing_studio
        for platform in request.json["platforms"] :
            existing_platform = Platform.query.filter(Platform.name.ilike(platform)).one_or_none()
            if existing_platform is None :
                game.platforms.append(Platform(platform))
            else:
                game.platforms.append(existing_platform)
        db.session.add(game)
        db.session.commit()
    except BaseException:
        print(f"{traceback.format_exc()}\n{sys.exc_info()[0]}")
        abort(400,'Invalid data')
    return f"{game.id}"

@app.route("/update", methods=['POST'])
def update():
    try:
        request.get_json(force=True)
        id = request.json["id"]
        # checking that the game exists
        game = Game.query.filter_by(id=id).first()
        if game is None :
            abort(404,"Unknown game")
        if "name" in request.json.keys() and request.json["name"] != "" and request.json["name"] != game.name :
            #check is name is not already in db
            if(Game.query.filter(Game.name.ilike(request.json["name"])).one_or_none() is not None):
                    abord("400","Game updated name is already knwon")
            game.name = request.json["name"]
        if "ratings" in request.json.keys() and request.json["ratings"] != "" :
            game.ratings = int(request.json["ratings"])
        if "studio" in request.json.keys() and request.json["studio"] != "" and request.json["studio"] != game.studio.name:
            old_studio = game.studio
            existing_studio = Studio.query.filter(Studio.name.ilike(request.json["studio"])).one_or_none()
            if existing_studio is None:
                game.studio = Studio(request.json["studio"])
            else:
                game.studio = existing_studio
            q = db.session.query(Game)
            q = q.filter(Game.id != game.id)
            q = q.filter(Game.studio.name == old_studio.name).limit(1)
            if q.one_or_none() is None:
                db.session.delete(old_studio)
        if "release_date" in request.json.keys() and request.json["release_date"] != "" :
            game.release_date = datetime.datetime.strptime(request.json["release_date"], "%Y-%m-%d").date()
        if "platforms" in request.json.keys() :
            old_platforms = [ platform for platform in game.platforms ]
            new_platforms = []
            for platform in request.json["platforms"]:
                existing_platform = Platform.query.filter(Platform.name.ilike(platform)).one_or_none()
                if(existing_platform is None):
                    new_platforms.append(Platform(platform))
                else:
                    new_platforms.append(existing_platform)
            game.platforms = new_platforms
            for platform in old_platforms:
                if platform not in new_platforms :
                    # check is still used
                    q = db.session.query(Game)
                    q = q.filter(Game.id != id)
                    q = q.filter(Game.platforms.any(Platform.name == platform.name)).limit(1)
                    used = q.one_or_none()
                    if used is None:
                        db.session.delete(platform)
        db.session.commit()
    except BaseException:
        print(f"{traceback.format_exc()}\n{sys.exc_info()[0]}")
        abort(400,'Invalid data')
    return f"{game.id}"

@app.route("/delete/<id>")
def delete(id):
    try:
        id = int(id)
        game = Game.query.filter_by(id=id).first()
        if(game is None):
            abort(404,"Unknwon game")
        db.session.delete(game)
        # check is studio has more than one game
        q = db.session.query(Game)
        q = q.filter(Game.id != game.id)
        q = q.filter(Game.studio_id == game.studio_id).limit(1)
        if q.one_or_none() is None:
            db.session.delete(game.studio)
        for platform in game.platforms:
            q = db.session.query(Game)
            q = q.filter(Game.id != game.id)
            q = q.filter(Game.platforms.any(Platform.name == platform.name)).limit(1)
            if q.one_or_none() is None:
                db.session.delete(platform)
        db.session.commit()
    except BaseException:
        print(f"{traceback.format_exc()}\n{sys.exc_info()[0]}")
        raise
    return f"{id}"
