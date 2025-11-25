from .base_service import BaseService
from repository.template_repository import TemplateRepo
from . import campaign_service
import nh3
from copy import deepcopy

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
    
    def get_by_id(self, id, fields = None, extra_fields = None, show_deleted = False):
        item = super().get_by_id(id, fields, extra_fields, show_deleted)
        if item:
            deletable = True
            cs = campaign_service.CampaignService(self.user_id)
            if cs.get_by_filter(group_id=id, limit=1):
                deletable = False
            item['can_be_deleted'] = deletable
        return item
    
    def clean_template_code(self, html:str):
        
        safe_css_properties = {
            'color','font-family','font-size','font-weight','font-style','text-align','text-decoration','text-transform','line-height','letter-spacing',
            'background-color','background-image','background-position','background-repeat',
            'border','border-color','border-width','border-style','border-radius','border-top','border-bottom','border-top','border-left','border-right',
            'margin','margin-top','margin-right','margin-bottom','margin-left','padding','padding-top','padding-right','padding-bottom','padding-left','width','height','max-width','max-height','min-width','min-height','display',
        }
        allowed_attributes = deepcopy(nh3.ALLOWED_ATTRIBUTES)
        allowed_attributes['*'] = {'style'}
        cleaner = nh3.Cleaner(
            filter_style_properties=safe_css_properties,
            attributes=allowed_attributes)
        return cleaner.clean(html)
