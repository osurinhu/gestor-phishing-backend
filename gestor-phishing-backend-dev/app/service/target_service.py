from .base_service import BaseService
from repository.target_repository import TargetRepo
from .campaign_service import CampaignService
from .group_service import GroupService

class TargetService(BaseService):
    def __init__(self, user_id:int):
        super().__init__(repo=TargetRepo(),
                         safe_fields=('id','creator_id','name','email','group_id',),
                         have_ownership=True,
                         user_id=user_id)




    def email_in_group(self, email:str, group_id:int, model_id:int=None)-> bool:
        target = self.get_by_filter(group_id=group_id, email=email)
        if not target:
            return False
        if not model_id:
            return True
        if target[0]['id'] != model_id:
            return True
        return False
    
    def code_in_group(self, code:str, group_id:int, model_id:int=None)-> bool:
        target = self.get_by_filter(group_id=group_id, person_code=code)
        if not target:
            return False
        if not model_id:
            return True
        if target[0]['id'] != model_id:
            return True
        return False

    def before_create(self, kwargs):
        if not GroupService(self.user_id).exists(kwargs['group_id']):
            raise ValueError
        if CampaignService(self.user_id).check_active_campaign(group_id=kwargs['group_id']):
            raise RuntimeError
        if self.email_in_group(email=kwargs['email'], group_id=kwargs['group_id']):
            raise FileExistsError('email')
        if self.code_in_group(code=kwargs['person_code'], group_id=kwargs['group_id']):
            raise FileExistsError('code')
        return super().before_create(kwargs)
    
    def before_update(self, model, kwargs):
        if not GroupService(self.user_id).exists(kwargs.get('group_id', model.group_id)):
            raise ValueError
        if CampaignService(self.user_id).check_active_campaign(group_id=model.group_id):
            raise RuntimeError
        if kwargs.get('email',None):
            if self.email_in_group(email=model.email, group_id=model.group_id, model_id=model.id):
                raise FileExistsError('email')
        if kwargs.get('person_code', None):
            if self.code_in_group(code=model.person_code, group_id=model.group_id, model_id=model.id):
                raise FileExistsError('code')

    
    def before_delete(self, model):
        if CampaignService(self.user_id).check_active_campaign(group_id=model.group_id):
            raise RuntimeError
        return super().before_delete(model)
