from .base_service import BaseService
from repository.campaign_repository import CampaignRepo
from datetime import date
from datetime import datetime
from . import group_service
from . import template_service
from nh3 import clean


class CampaignService(BaseService):
    def __init__(self, user_id:int):
        super().__init__(repo=CampaignRepo(),
                         safe_fields=(
                            'id',
                            'creator_id',
                            'group_id',
                            'template_id',
                            'name',
                            'description',
                            'active',
                            'start_date',
                            'end_date',
                            'send_time'),
                         have_ownership=True,
                         user_id=user_id)

    def check_active_campaign(self, **kwargs)-> bool:
        """Checks if theres a active campaign with kwargs parameters"""
        campaigns = self.get_by_filter(**kwargs)
        for campaign in campaigns:
            if campaign['active']:
                return True
        return False
    
    def validate_dates(self, start_date:date, end_date:date):
        if (start_date > end_date):
            raise ValueError('endstart')
        if (start_date < datetime.today()):
            raise ValueError('startpast')
        if (end_date < datetime.today()):
            raise ValueError('endpast')
        
    def before_create(self, kwargs):
        if not group_service.GroupService(self.user_id).exists(kwargs['group_id']):
            raise ValueError('group')
        if not template_service.TemplateService(self.user_id).exists(kwargs['template_id']):
            raise ValueError('template')
        self.validate_dates(start_date=kwargs['start_date'], end_date=kwargs['end_date'])

        kwargs['title_text'] = clean(kwargs['title_text'])
        kwargs['body_text'] = clean(kwargs['body_text'])

        return super().before_create(kwargs)
    
    def before_update(self, model):
        if not group_service.GroupService(self.user_id).exists(model.group_id):
            raise ValueError('group')
        if not template_service.TemplateService(self.user_id).exists(model.template_id):
            raise ValueError('template')
        if model.active == True:
            raise PermissionError('active')
        
        model.title_text = clean(model.title_text) 
        model.body_text = clean(model.body_text) 

        self.validate_dates(start_date=model.start_date, end_date=model.end_date)
        return super().before_update(model)
    
    def before_delete(self, model):
        if model.active == True:
            raise PermissionError('active')
        


        return super().before_delete(model)