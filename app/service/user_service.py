from base_service import BaseService
from repository.user_repository import UserRepo

repo = UserRepo()

class UserService():
    def __init__(self):
        super.__init__(self, repo)