from repository import base_repository

class BaseService:
    def __init__(self, repository: base_repository):
        self.repo = repository