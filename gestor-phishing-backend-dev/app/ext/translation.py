from flask_babel import Babel

babel = Babel()

def init_app(app):
    babel.init_app(app)