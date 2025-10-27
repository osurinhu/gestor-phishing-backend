from .base_repository import BaseRepo
from domain.models import User

class UserRepo(BaseRepo):
    def __init__(self):
        super().__init__(User)

    

