from ext.database import db
from domain.base import BaseModel
from sqlalchemy.exc import SQLAlchemyError

class BaseRepo:

    def __init__(self, model: BaseModel):
        self.model = model

    def add(self, obj: BaseModel) -> BaseModel:
        """Add a model object to the database"""
        try:
            db.session.add(obj)
            db.session.commit()
            db.session.refresh(obj)
            return obj
        except SQLAlchemyError as error:
            db.session.rollback()
            raise error

    def get_by_id(self, id: int) -> BaseModel:
        """Get a model element in the database by id"""
        return db.session.execute(db.select(self.model).where(self.model.id == id)).scalar_one_or_none()
    
    def update(self, obj: BaseModel, data: dict) -> BaseModel:
        try:
            for key, value in data.items():
                setattr(obj,key,value)
            db.session.commit()
            db.session.refresh(obj)
            return obj
        except SQLAlchemyError as error:
            db.session.rollback()
            raise error
    
    def delete(self, obj: BaseModel) -> BaseModel:
        try:
            db.session.delete(obj)
            db.session.commit()
            return obj
        except SQLAlchemyError as error:
            db.session.rollback()
            raise error