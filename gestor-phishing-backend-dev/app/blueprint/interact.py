from flask import Blueprint, redirect
from cryptography.fernet import Fernet
from dynaconf import settings
from datetime import datetime

from service.email_service import EmailService

blueprint = Blueprint('interact', __name__, url_prefix='/i')


@blueprint.route('/<id>')
def interact(id):
    try:
        cipher_suite = Fernet(settings.ENC_KEY)
        id = cipher_suite.decrypt(id).decode()
        EmailService().update(id, interacted=True, interaction_date=datetime.now())
    except:
         pass
    return redirect('https://www.youtube.com/error')


def init_app(app):
	app.register_blueprint(blueprint)