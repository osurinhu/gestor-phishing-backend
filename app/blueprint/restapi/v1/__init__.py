from ext.config import load_routes

from flask import Blueprint
from flask_restx import Api

from argparse import ArgumentTypeError
from email_validator import validate_email, EmailNotValidError
import json

blueprint = Blueprint('api', __name__, url_prefix='/api/v1')

api = Api(
    blueprint,
    title='API',
    version='V1',
    description='First version of the api')

class StrLen(object):
    def __init__(self, lenght:int, min:int=5):
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
    

def target(value):
    fields = {'target_name', 'target_email'}
    # Checks if value is a json
    try:
        value = json.loads(value)
    except:
        raise ArgumentTypeError("Target must be formated as {'target_name':'John Doe', 'target_email':'doejohn@mail.com'}")
    # Checks if value have the necessary fields
    if not fields.issubset(value):
        raise  ArgumentTypeError("Target must be formated as {'target_name':'John Doe', 'target_email':'doejohn@mail.com'}")
    # Checks if the email is valid
    try:
        value['target_email'] = validate_email(value['target_email']).normalized
    except:
        raise ArgumentTypeError(f'Email {value['target_email']} is invalid')
    return value

def init_app(app):
	load_routes(app, api)
	app.register_blueprint(blueprint)
