from flask_sqlalchemy import SQLAlchemy
from importlib import import_module
from domain.base import BaseModel


db = SQLAlchemy(model_class=BaseModel)

def init_app(app):
    db.init_app(app)

    import_module("domain.models")
