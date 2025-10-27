from .base_service import BaseService
from repository.user_repository import UserRepo
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash

class UserService(BaseService):
    def __init__(self):
        super().__init__(repo=UserRepo(),
                         safe_fields=('id','name','is_admin'))

    def create_model(self, name:str, password:str, is_admin:bool=False):
        password = generate_password_hash(password)
        return super().create_model(name=name, password=password, is_admin=is_admin)

    def auth_user(self, name:str, password:str)-> str:
        try:
            user = self.repo.get_by_filter(name=name, query_limit=1)[0]
        except:
            return None
        if not check_password_hash(user.password, password):
            return None
        return create_access_token(user)
    