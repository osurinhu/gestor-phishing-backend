from ext.database import db

from service import user_service
from service import campaign_service

from cryptography.fernet import Fernet
import click

def create_db():
    """Creates database"""
    db.create_all()
    print('Database created!')

def drop_db():
    """Drops database"""
    db.drop_all()
    print('Database droppd!')

def enc_key():
    """Generates fernet cryptography key"""
    print(Fernet.generate_key().decode())

def add_admin():
    service = user_service.UserService()
    admin = service.get_by_filter(name='admin')
    if admin:
        print("Admin already exists!")
        return
    service.create(name='admin', password='teste', is_admin=True)
    print('Admin added!')

@click.argument('id', type=int)
def run_campaign(id):
    """Runs a campaign"""
    try:
        campaign_service.run_campaign(id)
    except ValueError as e:
        if e.args:
            if e.args[0] == 'id':
                print(f'Cant find campaign with the id {id}')
    except RuntimeError as e:
        if e.args:
            if e.args[0] == 'status':
                print('The campaign cannot be carried out. Perhaps it does not have the "i" status.')

@click.argument('id', type=int)
def end_campaign(id):
    """Ends a camapign"""
    try:
        campaign_service.end_campaign(id)
    except ValueError as e:
        if e.args:
            if e.args[0] == 'id':
                print(f'Cant find campaign with the id {id}')
    except RuntimeError as e:
        if e.args:
            if e.args[0] == 'status':
                print('The campaign cannot be ended. Perhaps its not active!')

'''
def populate_db():
'''

def init_app(app):
    for command in [create_db, drop_db, add_admin, enc_key, run_campaign, end_campaign]:
        app.cli.add_command(app.cli.command()(command))