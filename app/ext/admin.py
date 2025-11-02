from flask_admin import Admin
from flask_admin.base import AdminIndexView
from flask_admin.contrib import sqla

from ext.database import db
from ext.auth import admin_required

from service.user_service import UserService

from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash

from domain.models import User, Campaign

AdminIndexView._handle_view = admin_required(AdminIndexView._handle_view)
sqla.ModelView._handle_view = admin_required(sqla.ModelView._handle_view)


class CustomModelView(ModelView):
    form_excluded_columns = ('created_at', 'last_update', 'deleted')

class UserView(CustomModelView):
    column_exclude_list = ('password')

    form_args = dict(
        password=dict(render_kw={'value':'', 'type':'password'})
    )

    def on_model_change(self, form, model, is_created):
        model.password = generate_password_hash(model.password)

    def delete_model(self, model):
        service = UserService()
        service.delete(model.id)

admin = Admin()

def init_app(app):

    admin.name = app.config.TITLE
    admin.add_views(UserView(User, db.session))
    admin.add_views(UserView(Campaign, db.session))
    admin.init_app(app)