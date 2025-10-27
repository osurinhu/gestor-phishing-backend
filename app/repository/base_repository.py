from ext.database import db
from domain.base import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from typing import List

class BaseRepo:

    def __init__(self, model:BaseModel):
        self.model = model
        

    def add(self, model:BaseModel, commit:bool=True)-> BaseModel:
        """Add a model object to the database"""
        try:
            db.session.add(model)
            if commit:
                db.session.commit()
            else:
                db.session.flush([model])
            db.session.refresh(model)
            return model
        except SQLAlchemyError as error:
            db.session.rollback()
            raise error
        

    def get_by_id(self, id:int)-> BaseModel:
        """Get a model element in the database by id"""
        return db.session.execute(db.select(self.model).where(self.model.id == id)).scalar_one_or_none()
    
    def update(self, model:BaseModel, data:dict) -> BaseModel:
        try:
            for key, value in data.items():
                setattr(model,key,value)
            db.session.commit()
            db.session.refresh(model)
            return model
        except SQLAlchemyError as error:
            db.session.rollback()
            raise error
    
    def delete(self, model:BaseModel)-> BaseModel:
        return self.update(model=model, data={'deleted':True})

    def hard_delete(self, model: BaseModel)-> BaseModel:
        try:
            db.session.delete(model)
            db.session.commit()
            return model
        except SQLAlchemyError as error:
            db.session.rollback()
            raise error
        
    def get_by_filter(self, query_limit:int=100, **kwargs)-> List[BaseModel]:
        try:
            stmt = db.select(self.model).filter_by(**kwargs).limit(query_limit)
            return db.session.execute(stmt).scalars().all()
        except SQLAlchemyError as error:
            return error

    def commit(self):
        db.session.commit()

    def rollback(self):
        db.session.rollback()