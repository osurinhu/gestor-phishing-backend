from flask_apscheduler import APScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

scheduler = APScheduler()

def init_app(app):

    scheduler.init_app(app)
    
    scheduler.start()