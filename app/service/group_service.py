from .base_service import BaseService
from repository.group_repository import GroupRepo
from . import campaign_service

class GroupService(BaseService):
    def __init__(self, user_id:int):
        super().__init__(repo=GroupRepo(),
                         safe_fields=('id','creator_id','name','description',),
                         have_ownership=True,
                         user_id=user_id)
        
    def before_delete(self, model):
        if campaign_service.CampaignService(self.user_id).check_active_campaign(group_id=model.id):
            raise RuntimeError
        return super().before_delete(model)