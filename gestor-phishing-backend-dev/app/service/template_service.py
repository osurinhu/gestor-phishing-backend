from .base_service import BaseService
from repository.template_repository import TemplateRepo
from . import campaign_service
from nh3 import Cleaner

class TemplateService(BaseService):
    def __init__(self, user_id:int):
        super().__init__(repo=TemplateRepo(),
                         safe_fields=(
                            'id',
                            'creator_id',
                            'name',
                            'description'),
                         have_ownership=True,
                         user_id=user_id)


    def clean_template_code(self, html=str):
        html = Cleaner().clean(html)
        return html
    
    def before_create(self, kwargs):
        kwargs['code'] = self.clean_template_code(kwargs['code'])
        return super().before_create(kwargs)
    
    def before_update(self, model):
        if campaign_service.CampaignService(self.user_id).check_active_campaign(template_id=model.id):
            raise RuntimeError
        model.code = self.clean_template_code(model.code)

    def before_put(self, new_entry, old_model):
        cs = campaign_service.CampaignService(self.user_id)
        campaigns = cs.get_by_filter(template_id=old_model.id)
        for campaign in campaigns:
            if campaign['status'] == 'i':
                cs.update(campaign['id'], template_id=new_entry['id'], commit=False)

    def before_delete(self, model):
        if campaign_service.CampaignService(self.user_id).check_active_campaign(template_id=model.id):
            raise RuntimeError
        return super().before_delete(model)