from ext.database import db

from domain.models import User
from service.user_service import UserService

def create_db():
    """Creates database"""
    db.create_all()

def drop_db():
    """Cleans database"""
    db.drop_all()

def add_admin():
    service = UserService()
    foo = service.get_by_filter(name='admin')
    if foo:
        print("Admin already exists!")
        return
    service.add_new_model(name='admin', password='teste', is_admin=True)
    print('Admin added!')
'''
def populate_db():
'''

def init_app(app):
    for command in [create_db, drop_db, add_admin]:
        app.cli.add_command(app.cli.command()(command))