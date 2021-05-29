#!/usr/bin/env python

from flask.cli import FlaskGroup

from src.app import app
from src.db import db

cli = FlaskGroup(app)


@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


if __name__ == "__main__":
    cli()
