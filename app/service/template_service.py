from .base_service import BaseService
from repository.template_repository import TemplateRepo
from .campaign_service import CampaignService
from nh3 import Cleaner

class TemplateService(BaseService):
    def __init__(self, user_id:int):
        super().__init__(repo=TemplateRepo(),
                         safe_fields=(
                            'id',
                            'creator_id',
                            'name',
                            'description',
                            'code'),
                         have_ownership=True,
                         user_id=user_id)


    def clean_template_code(self, html=str):
        html = Cleaner().clean(html)
        return html
    
    def before_create(self, kwargs):
        kwargs['code'] = self.clean_template_code(kwargs['code'])
        return super().before_create(kwargs)
    
    def before_update(self, model):
        if CampaignService(self.user_id).check_active_campaing(template_id=model.id):
            raise RuntimeError
        model.code = self.clean_template_code(model.code)
        return super().before_update(model)
    
    def before_delete(self, model):
        if CampaignService(self.user_id).check_active_campaing(template_id=model.id):
            raise RuntimeError
        return super().before_delete(model)