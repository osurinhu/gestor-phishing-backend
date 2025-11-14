from .base_repository import BaseRepo
from domain.models import Template

class TemplateRepo(BaseRepo):
    def __init__(self):
        super().__init__(Template)
