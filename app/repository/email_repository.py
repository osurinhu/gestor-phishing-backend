from .base_repository import BaseRepo
from domain.models import EmailSent

class EmailRepo(BaseRepo):
    def __init__(self):
        super().__init__(EmailSent)