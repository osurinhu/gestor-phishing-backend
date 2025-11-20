from .base_service import BaseService

from flask import url_for
from repository.campaign_repository import CampaignRepo
from datetime import datetime, date, time
from nh3 import clean
from jinja2 import Template
from cryptography.fernet import Fernet
from dynaconf import settings

from . import group_service
from . import template_service
from . import email_service

from ext.jobs import scheduler

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
                            'sender_email',
                            'status',
                            'start_date',
                            'end_date',
                            'send_time'),
                         have_ownership=True,
                         user_id=user_id)
        
    def set_jobs(self, id, start_date, send_time, end_date):
        start_dt = datetime.combine(
            datetime.strptime(start_date, '%Y-%m-%d').date(),
            datetime.strptime(send_time, '%H:%M').time())

        end_dt = datetime.combine(datetime.strptime(end_date, '%Y-%m-%d').date(), time(0, 0))

        scheduler.add_job(
            func=run_campaign,
            trigger='date',
            run_date=start_dt,
            id=f'camp_{id}_start',
            args=[id],
            replace_existing=True,
            misfire_grace_time=30
        )

        scheduler.add_job(
            func=end_campaign,
            trigger='date',
            run_date=end_dt,
            id=f'camp_{id}_end',
            args=[id],
            replace_existing=True,
            misfire_grace_time=30
        )
    
    def validate_dates(self, start_date, end_date):
        if start_date >= end_date:
            raise ValueError('endstart')
        if start_date <= date.today():
            raise ValueError('startpast')
        if end_date <= date.today():
            raise ValueError('endpast')

    def before_create(self, kwargs):
        if not group_service.GroupService(self.user_id).exists(kwargs['group_id']):
            raise ValueError('group')
        if not template_service.TemplateService(self.user_id).exists(kwargs['template_id']):
            raise ValueError('template')
        self.validate_dates(start_date=kwargs['start_date'], end_date=kwargs['end_date'])

        kwargs['title_text'] = clean(kwargs['title_text'])
        kwargs['body_text'] = clean(kwargs['body_text'])
        kwargs['button_text'] = clean(kwargs['button_text'])
        return super().before_create(kwargs)
    
    def create(self, commit = True, **kwargs):
        campaign = super().create(commit, **kwargs)
        self.set_jobs(campaign['id'], campaign['start_date'], campaign['send_time'], campaign['end_date'])
        return campaign

    def before_update(self, model, kwargs):
        if model.status in ('a','f'):
            raise PermissionError('active')
        if kwargs.get('group_id', None):
            if not group_service.GroupService(self.user_id).exists(model.group_id):
                raise ValueError('group')
        if kwargs.get('template_id', None):
            if not template_service.TemplateService(self.user_id).exists(model.template_id):
                raise ValueError('template')
            
        kwargs['title_text'] = clean(kwargs.get('title_text', None) or model.title_text) 
        kwargs['body_text'] = clean(kwargs.get('body_text', None) or model.body_text) 
        kwargs['button_text'] = clean(kwargs.get('button_text', None) or model.button_text) 

        self.validate_dates(start_date=kwargs.get('start_date',None) or model.start_date,
                            end_date=kwargs.get('end_date', None) or model.end_date)

    
    def update(self, id, commit = True, **kwargs):
        campaign = super().update(id, commit, **kwargs)
        self.set_jobs(campaign['id'], campaign['start_date'], campaign['send_time'], campaign['end_date'])
        return campaign

    def before_delete(self, model):
        if model.status in ('a','f'):
            raise PermissionError('active')
        return super().before_delete(model)

def end_campaign(campaign_id:int):
    with scheduler.app.app_context():
        cs = CampaignService(0)
        campaign = cs.repo.get_by_id(id=campaign_id)
        if not campaign:
            raise ValueError('id')
        if campaign.status != 'a':
            raise RuntimeError('status')
        cs.repo.update(campaign, status='f')
        try:
            scheduler.remove_job(f'camp_{campaign_id}_end')
        except:
            pass

def run_campaign(campaign_id:int):
    with scheduler.app.app_context():
        cs = CampaignService(0)
        campaign = cs.repo.get_by_id(campaign_id)
        if not campaign:
            raise ValueError('id')
        if campaign.deleted or campaign.status != 'i':
            raise RuntimeError('status')
        cs.update(id=campaign_id, status='a')
        
        template = Template(campaign.template.code)

        es = email_service.EmailService()
        cipher_suite = Fernet(settings.ENC_KEY)

        with email_service.Smtp() as smtp:
            for target in campaign.group.group_member:
                log = es.create(target_id=target.id,campaign_id=campaign_id)
                log_enc = cipher_suite.encrypt(str(log['id']).encode()).decode()

                link = url_for('interact.interact', id=log_enc)
                mail = template.render(title_text=campaign.title_text,
                                    button_text=campaign.button_text,
                                    body_text=campaign.body_text,
                                    name=target.name,
                                    link=link)
                
                es.send_mail(sender=campaign.sender_email, recipient=target.email, subject=campaign.subject_text, mail=mail, smtp=smtp)
            
        try:
            scheduler.remove_job(f'camp_{campaign_id}_start')
        except:
            pass

