from flask import Blueprint, jsonify, make_response
from werkzeug.exceptions import NotFound

blueprint = Blueprint('error_handler', __name__, )


@blueprint.app_errorhandler(Exception)
def error500(error):
	return make_response(jsonify(error=500, message='Internal Error'), 500)

@blueprint.app_errorhandler(NotFound)
def error400(error):
	return make_response(jsonify(error=404, message='Not Found'), 404)


def init_app(app):
	app.register_blueprint(blueprint)