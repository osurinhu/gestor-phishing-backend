from .base_service import BaseService
from repository.campaign_repository import CampaignRepo

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
                            'send_time',
                            'subject_text',
                            'title_text',
                            'body_text'),
                         have_ownership=True,
                         user_id=user_id)

    def check_active_campaing(self, **kwargs)-> bool:
        """Checks if theres a active campaing with kwargs parameters"""
        campaings = self.get_by_filter(**kwargs)
        for campaing in campaings:
            if campaing['active']:
                return True
        return False