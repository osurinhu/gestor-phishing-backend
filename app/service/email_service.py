from .base_service import BaseService
from repository.email_repository import EmailRepo

from email.message import EmailMessage
import smtplib

class EmailService(BaseService):
    def __init__(self):
        super().__init__(repo=EmailRepo(),
                         safe_fields=('id','target_id','campaign_id','interacted','interaction_date', 'target.name', 'target.email', 'target.person_code'),
                         can_be_deleted=False
                         )  

    def send_mail(self,sender,recipient,subject,mail, smtp=None):
        msg = EmailMessage()
        msg.add_alternative(mail, subtype='html')

        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = recipient

        if smtp:
            smtp.send_message(msg)
            return

        with Smtp() as smtp:
            smtp.send_message(msg)
        return
        
class Smtp:
    def __init__(self, host='smtp.freesmtpservers.com', port=25):
        self.host = host
        self.port = port
        self.server = None

    def __enter__(self):
        self.server = smtplib.SMTP(self.host, self.port)
        self.server.ehlo()  
        return self.server

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.server:
            try:
                self.server.quit()
            except Exception:
                self.server.close()
