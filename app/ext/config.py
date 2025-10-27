from importlib import import_module
from dynaconf import FlaskDynaconf

def init_app(app):
    FlaskDynaconf(app)

def load_extensions(app):
    for extensao in app.config.get("EXTENSOES"):
        modulo = import_module(extensao)
        modulo.init_app(app)

def load_routes(app, api):
    for route in app.config.get(api.title+api.version):
        module = import_module(route)
        api.add_namespace(module.ns)