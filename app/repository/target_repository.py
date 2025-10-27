from .base_repository import BaseRepo
from domain.models import Target

class TargetRepo(BaseRepo):
    def __init__(self):
        super().__init__(Target)
