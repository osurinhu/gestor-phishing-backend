from flask_admin import Admin
from ext.database import db
from flask_admin.contrib.sqla import ModelView
from domain.models import User


class UserView(ModelView):
    column_exclude_list = ('password',)


admin = Admin()

def init_app(app):
    admin.add_views(UserView(User, db.session))
    admin.init_app(app)