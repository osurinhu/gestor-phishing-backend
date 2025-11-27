from ext.config import load_routes

from flask import Blueprint
from flask_restx import Api, reqparse

from argparse import ArgumentTypeError
from email_validator import validate_email, EmailNotValidError
import json
from datetime import datetime

blueprint = Blueprint('apiv1', __name__, url_prefix='/api/v1')

authorizations={
    'bearerAuth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'Enter your Bearer token in the format **Bearer <token>**'
    }
}

api = Api(
    blueprint,
    title='API',
    version='V1',
    description='First version of the api',
    validate=True,
    authorizations=authorizations)

class StrLen(object):
    def __init__(self, lenght:int, min:int=1):
         self.lenght = lenght
         self.min = min
    def __call__(self, value):
        try:
            value = str(value)
        except:
            raise ArgumentTypeError('Argument must be a valid string') 
        if (len(value) > self.lenght):
            raise ArgumentTypeError(f'Argument must have a maximum lenght of {self.lenght} characters')
        if (len(value) < self.min):
            raise ArgumentTypeError(f'Argument must have a minimum lenght of {self.min} characters')
        return value

def email(value):
    try:
        value = validate_email(value).normalized
    except:
        raise ArgumentTypeError(f'Email {value} is invalid')
    return value

def target(value):
    fields = {'name', 'email', 'person_code'}
    # Checks if value is a json
    try:
        value = json.loads(value)
    except:
        raise ArgumentTypeError("Target must be formated as {'name':'John Doe', 'person_code':'john#312', 'email':'doejohn@mail.com'}")
    # Checks if value have the necessary fields
    if not fields.issubset(value):
        raise ArgumentTypeError("Target must be formated as {'name':'John Doe', 'person_code':'john#312', 'email':'doejohn@mail.com'}")
    
    # Checks if the email is valid
    value['name'] = StrLen(25).__call__(value['name'])

    value['email'] = email(value['email'])

    value['person_code'] = StrLen(25, 1).__call__(value['person_code'])

    return value

target.__schema__ = {'type':'json', 'format':"{'name':'John Doe', 'person_code':'john#312', 'email':'doejohn@mail.com'}"}

def group_id(value):
    try:
        value = int(value)
    except:
        raise ArgumentTypeError("Value must be an integer")
    

def timeO(value):
    try:
        # Parse the string into a datetime object, then extract the time part
        return datetime.strptime(value, '%H:%M').time()
    except ValueError:
        raise ArgumentTypeError(f"Time '{value}' must be in HH:MM format")

def dateO(value):
    """Parse a valid looking date in the format YYYY-mm-dd"""
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except:
        raise ArgumentTypeError(f"Date '{value}' must be in YYYY-MM-DD format")

page_args = reqparse.RequestParser()
page_args.add_argument("page", type=int, help="The current page of the query", location='args', required=False, default=1)
page_args.add_argument("per_page", type=int, help="The max number of elements per page", location='args', required=False, default=20)


def init_app(app):
	load_routes(app, api)
	app.register_blueprint(blueprint)
