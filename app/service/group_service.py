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
        cs = campaign_service.CampaignService(self.user_id)
        if cs.get_by_filter(group_id=model.id, limit=1):
            raise RuntimeError
        return super().before_delete(model)
    
    def get_by_id(self, id, fields = None, extra_fields = None, show_deleted = False):
        item = super().get_by_id(id, fields, extra_fields, show_deleted)
        if item:
            deletable = True
            cs = campaign_service.CampaignService(self.user_id)
            if cs.get_by_filter(group_id=id, limit=1):
                deletable = False
            item['can_be_deleted'] = deletable
        return item