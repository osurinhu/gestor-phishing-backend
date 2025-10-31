from ext.database import db
from domain.base import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from flask_sqlalchemy.pagination import Pagination
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

    def get_by_filter(self, limit:int=20, **kwargs)-> List[BaseModel]:
        if limit>100:
            limit=100
        try:
            stmt = db.select(self.model).filter_by(**kwargs).limit(limit)
            return db.session.execute(stmt).scalars().all()
        except SQLAlchemyError as error:
            return error
    
    def get_page_by_filter(self, page:int=1, per_page:int=20, **kwargs)-> Pagination:
        try:
            stmt = db.select(self.model).filter_by(**kwargs)
            pages = db.paginate(stmt, page=page, per_page=per_page, max_per_page=100)
            return pages
        except SQLAlchemyError as error:
            return error
    
    def update(self, model:BaseModel, commit:bool=True, **kwargs) -> BaseModel:
        try:
            for key, value in kwargs.items(): 
                if value:
                    setattr(model,key,value)
            if commit:
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
        
    def commit(self):
        db.session.commit()

    def rollback(self):
        db.session.rollback()