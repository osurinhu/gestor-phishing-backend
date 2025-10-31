from repository import base_repository
from domain.base import BaseModel
from typing import Iterable, Any

class BaseService:
    def __init__(self, repo: base_repository, safe_fields:tuple=tuple()):
        self.repo = repo
        self.safe_fields = safe_fields + ('deleted',)
    
    def create(self, commit:bool=True, **kwargs)-> dict:
        return self.add_model(self.create_model(**kwargs),commit=commit)
    
    def create_many(self, items:Iterable[dict[str,Any]], commit:bool=True, **kwargs)-> tuple[int]:
        """Try to create and add all the models in the iterable
            Rollback all if one fail
            Returns a tuple with all the models id"""
        return self.add_many_models(self.create_many_models(items=items, **kwargs),commit=commit)
    
    def create_model(self, **kwargs)-> BaseModel:
        """
        Create an model object of the repository model.\n
        Applies business logic before creation\n
        Returns an model object.
        """
        return self.repo.model(**kwargs)
    
    def create_many_models(self, items:Iterable[dict[str,Any]], **kwargs)-> tuple[BaseModel]:
        """Try to create all the models in the iterable
            Raises RuntimeError if one fails"""
        try:
            models = tuple()
            for item in items:
                model = self.create_model(**item, **kwargs)
                models += (model,)
            return models
        except:
            raise RuntimeError
    
    def add_model(self, model:BaseModel, commit:bool=True)-> dict:
        return self.repo.add(model, commit=commit).to_dict(self.safe_fields)
    
    def add_many_models(self, models:Iterable[BaseModel], commit:bool=True)-> tuple[int]:
        """Try to add all the models in the iterable
            Rollback all if one fail
            Returns a tuple with all the models id"""
        try:
            inserted_ids = tuple()
            for model in models:
                model = self.add_model(model, commit=commit)
                inserted_ids += (model['id'],)
        except:
            self.repo.rollback()
            raise ValueError
        if commit:
            self.repo.commit()
        return inserted_ids
            
    def delete(self, id:int)-> dict:
        model = self.repo.get_by_id(id)
        return self.repo.delete(model).to_dict(self.safe_fields)

    def get_by_id(self, id:int, fields:list=None)-> dict:
        if not fields:
            fields=self.safe_fields
        return self.repo.get_by_id(id).to_dict(fields)
    
    def get_by_filter(self, fields:list=None, limit:int=50, show_deleted:bool=False, **kwargs)-> dict:
        """Returns a list with the query elements"""
        if not fields:
            fields=self.safe_fields
        if not show_deleted:
            kwargs['deleted'] = False
        values = self.repo.get_by_filter(**kwargs)
        serialized = []
        for value in values:
            serialized.append(value.to_dict(only=self.safe_fields))
        return serialized

    def get_page_filtered(self, fields:list=None, page:int=1, per_page:int=20, **kwargs)-> dict:
        if not fields:
            fields=self.safe_fields
        p = self.repo.get_page_by_filter(page=page, per_page=per_page, **kwargs)
        items = []
        for item in p:
            items.append(item.to_dict(only=fields))
        return {
            'items': items,
            'current_page': p.page,
            'total_of_items': p.total,
            'total_of_pages': p.pages,
            'has_prev': p.has_prev,
            'has_prev': p.has_next,
        }

    def update(self, model_id:int, user_id:int, commit:bool=True, **kwargs):
        model = self.repo.get_by_id(id=model_id)
        try:
            if model.creator_id != user_id:
                raise PermissionError
        except AttributeError:
            raise NotImplementedError
        args = dict()
        for key, value in kwargs.items(): 
            if value:
                args[key] = value
        return self.repo.update(model=model, commit=commit, **args).to_dict(self.safe_fields)

    def commit(self):
        return self.repo.commit()
    
    def rollback(self):
        return self.repo.rollback()