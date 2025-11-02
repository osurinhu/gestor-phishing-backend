from .base_service import BaseService
from repository.group_repository import GroupRepo
from .campaign_service import CampaignService

class GroupService(BaseService):
    def __init__(self, user_id:int):
        super().__init__(repo=GroupRepo(),
                         safe_fields=('id','creator_id','name','description',),
                         have_ownership=True,
                         user_id=user_id)
        
    def before_delete(self, model):
        if CampaignService(self.user_id).check_active_campaing(group_id=model.id):
            raise RuntimeError
        return super().before_delete(model)