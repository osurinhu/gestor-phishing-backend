from ext.database import db
from datetime import date
from .base_repository import BaseRepo
from domain.base import BaseModel
from domain.models import Campaign
from sqlalchemy.exc import SQLAlchemyError

class CampaignRepo(BaseRepo):
    def __init__(self):
        super().__init__(Campaign)

    def get_ending_soon(self, creator_id:int) -> BaseModel:
        try:
            stmt = db.select(self.model).where(
                self.model.end_date > date.today(),
                self.model.creator_id == creator_id,
                self.model.deleted == 0
            ).order_by(self.model.end_date).limit(1)
            return db.session.execute(stmt).scalar_one_or_none()
        except SQLAlchemyError as error:
            raise error