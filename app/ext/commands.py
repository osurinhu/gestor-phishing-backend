from ext.database import db

from service import user_service
from service import campaign_service
from service import email_service

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
def run_campaing(id):
    """Runs a campaign"""
    campaign_service.run_campaign(id)

@click.argument('id', type=int)
def end_campaign(id):
    """Ends a camapign"""
    campaign_service.end_campaign(id)
    
def test_mail():
    service = email_service.EmailService()
    service.send_mail(recipient='antoniodepaduarabelo767@gmail.com', subject='teste', mail='<html><body>superteste</body></html>')

    
'''
def populate_db():
'''

def init_app(app):
    for command in [create_db, drop_db, add_admin, enc_key, run_campaing, end_campaign, test_mail]:
        app.cli.add_command(app.cli.command()(command))