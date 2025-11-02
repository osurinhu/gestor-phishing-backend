from .base_service import BaseService
from repository.target_repository import TargetRepo
from .campaign_service import CampaignService

class TargetService(BaseService):
    def __init__(self, user_id:int):
        super().__init__(repo=TargetRepo(),
                         safe_fields=('id','creator_id','name','email','group_id',),
                         have_ownership=True,
                         user_id=user_id)


    def before_create(self, kwargs):
        if CampaignService(self.user_id).check_active_campaing(group_id=kwargs['group_id']):
            raise RuntimeError
        return super().before_create(kwargs)
    
    def before_update(self, model):
        if CampaignService(self.user_id).check_active_campaing(group_id=model.group_id):
            raise RuntimeError
        return super().before_update(model)
    
    def before_delete(self, model):
        if CampaignService(self.user_id).check_active_campaing(group_id=model.group_id):
            raise RuntimeError
        return super().before_delete(model)
