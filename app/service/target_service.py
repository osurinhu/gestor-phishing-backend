from .base_service import BaseService
from repository.target_repository import TargetRepo
from .campaign_service import CampaignService
from .group_service import GroupService
from service import email_service

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
        if self.email_in_group(email=kwargs['email'], group_id=kwargs['group_id']):
            raise FileExistsError('email')
        if self.code_in_group(code=kwargs['person_code'], group_id=kwargs['group_id']):
            raise FileExistsError('code')
        return super().before_create(kwargs)
    
    def before_update(self, model, kwargs):
        if not GroupService(self.user_id).exists(kwargs.get('group_id', model.group_id)):
            raise ValueError
        if kwargs.get('email',None):
            if self.email_in_group(email=model.email, group_id=model.group_id, model_id=model.id):
                raise FileExistsError('email')
        if kwargs.get('person_code', None):
            if self.code_in_group(code=model.person_code, group_id=model.group_id, model_id=model.id):
                raise FileExistsError('code')

    def before_delete(self, model):
        emails = email_service.EmailService().get_by_filter(target_id=model.id)
        if emails:
            cs = CampaignService(self.user_id)
            for email in emails:
                if cs.get_by_filter(id=email['campaign_id']):
                    raise RuntimeError
        return super().before_delete(model)
    
    def get_by_id(self, id, fields = None, extra_fields = None, show_deleted = False):
        item = super().get_by_id(id, fields, extra_fields, show_deleted)
        if item:
            deletable = True
            es = email_service.EmailService()
            if es.get_by_filter(target_id=id, limit=1):
                for campaign in es.get_by_filter(target_id=item['id'], fields=('from_campaign.deleted',)):
                    if not campaign['from_campaign']['deleted']:
                        deletable = False
            item['can_be_deleted'] = deletable
        return item