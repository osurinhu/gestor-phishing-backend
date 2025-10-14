from ext.database import db

from domain.models import User
from repository.user_repository import UserRepo

def create_db():
    """Creates database"""
    db.create_all()

def drop_db():
    """Cleans database"""
    db.drop_all()

def test_db():
    repo = UserRepo()
    u = User(name='nometeste', password='senhateste')
    a = repo.add(u)
    q = repo.get_by_id(a.id)
    print(q)

'''
def populate_db():
'''

def init_app(app):
    for command in [create_db, drop_db, test_db]:
        app.cli.add_command(app.cli.command()(command))