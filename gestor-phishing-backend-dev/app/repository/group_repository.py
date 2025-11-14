from .base_repository import BaseRepo
from domain.models import Group

class GroupRepo(BaseRepo):
    def __init__(self):
        super().__init__(Group)
