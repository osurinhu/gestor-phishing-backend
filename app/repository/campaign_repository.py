from .base_repository import BaseRepo
from domain.models import Campaign

class CampaignRepo(BaseRepo):
    def __init__(self):
        super().__init__(Campaign)
