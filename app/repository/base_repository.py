from ext.database import db
from domain.base import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from flask_sqlalchemy.pagination import Pagination
from typing import List

class BaseRepo:

    def __init__(self, model:BaseModel):
        self.model = model

    def add(self, model:BaseModel)-> BaseModel:
        """Add a model object to the database"""
        try:
            db.session.add(model)
            db.session.flush([model])
            db.session.refresh(model)
            return model
        except SQLAlchemyError as error:
            db.session.rollback()
            raise error
        
    def get_by_id(self, id:int)-> BaseModel:
        """Get a model element in the database by id"""
        return db.session.execute(db.select(self.model).where(self.model.id == id)).scalar_one_or_none()

    def get_by_filter(self, limit:int=None, **kwargs)-> List[BaseModel]:
        try:
            stmt = db.select(self.model).filter_by(**kwargs)
            if limit:
                stmt = stmt.limit(limit)
            return db.session.execute(stmt).scalars().all()
        except SQLAlchemyError as error:
            raise error
    
    def get_page_by_filter(self, exact:dict, like:dict, page:int=1, per_page:int=20)-> Pagination:
        try:
            stmt = db.select(self.model).filter_by(**exact)
            for key, value in like.items():
                if value != None or value != '':
                    stmt = stmt.where(getattr(self.model, key).like("%"+str(value)+"%"))
            pages = db.paginate(stmt, page=page, per_page=per_page, max_per_page=100)
            return pages
        except SQLAlchemyError as error:
            raise error
    
    def update(self, model:BaseModel, **kwargs) -> BaseModel:
        try:
            for key, value in kwargs.items(): 
                if value:
                    setattr(model,key,value)
            db.session.flush([model])
            db.session.refresh(model)
            return model
        except SQLAlchemyError as error:
            db.session.rollback()
            raise error
    
    def delete(self, model:BaseModel)-> BaseModel:
        return self.update(model=model, deleted=True)
        
    def commit(self):
        db.session.commit()

    def rollback(self):
        db.session.rollback()