from flask import Blueprint, abort

blueprint = Blueprint('error_handler', __name__, )


@blueprint.app_errorhandler(Exception)
def error500(error):
	return abort(500, 'Internal error')

def init_app(app):
	app.register_blueprint(blueprint)