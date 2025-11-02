from .base_service import BaseService
from repository.user_repository import UserRepo
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash

class UserService(BaseService):
    def __init__(self):
        super().__init__(repo=UserRepo(),
                         safe_fields=('id','name','is_admin'))

    def before_create(self, kwargs):
        kwargs['password'] = generate_password_hash(kwargs['password'])

    def auth_user(self, name:str, password:str)-> str:
        try:
            user = self.repo.get_by_filter(name=name, limit=1)[0]
        except:
            return None
        if not check_password_hash(user.password, password):
            return None
        return create_access_token(user)
    