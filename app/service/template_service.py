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
        html = Cleaner(url_schemes=set('{{link}}')).clean(html)
        return html
    
    def before_create(self, kwargs):
        kwargs['code'] = self.clean_template_code(kwargs['code'])
        return super().before_create(kwargs)
    

    def before_put(self, new_entry, old_model):
        cs = campaign_service.CampaignService(self.user_id)
        campaigns = cs.get_by_filter(template_id=old_model.id)
        for campaign in campaigns:
            if campaign['status'] == 'i':
                cs.update(campaign['id'], template_id=new_entry['id'], commit=False)

    def before_delete(self, model):
        if campaign_service.CampaignService(self.user_id).get_by_filter(template_id=model.id, limit=1):
            raise RuntimeError
        return super().before_delete(model)

    def get_page_filtered(self, fields = None, extra_fields = None, page = 1, per_page = 20, exact:dict=dict(), **kwargs):
        p =  super().get_page_filtered(fields, extra_fields, page, per_page, exact, **kwargs)
        cs = campaign_service.CampaignService(self.user_id)
        for item in p['items']:
            deletable = True
            if cs.get_by_filter(group_id=item['id'], limit=1):
                deletable = False
            item['can_be_deleted'] = deletable
        return p
    
    def get_by_id(self, id, fields = None, extra_fields = None, show_deleted = False):
        item = super().get_by_id(id, fields, extra_fields, show_deleted)
        if item:
            deletable = True
            cs = campaign_service.CampaignService(self.user_id)
            if cs.get_by_filter(group_id=id, limit=1):
                deletable = False
            item['can_be_deleted'] = deletable
        return item