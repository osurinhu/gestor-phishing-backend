from ext.database import db

from domain.models import User
from service.user_service import UserService

def create_db():
    """Creates database"""
    db.create_all()
    print('Database created!')

def drop_db():
    """Drops database"""
    db.drop_all()
    print('Database droppd!')

def add_admin():
    service = UserService()
    admin = service.get_by_filter(name='admin')
    if admin:
        print("Admin already exists!")
        return
    service.create(name='admin', password='teste', is_admin=True)
    print('Admin added!')
    
'''
def populate_db():
'''

def init_app(app):
    for command in [create_db, drop_db, add_admin]:
        app.cli.add_command(app.cli.command()(command))