from repository import base_repository
from domain.base import BaseModel
from typing import Iterable, Any

class BaseService:
    def __init__(self, repo: base_repository, safe_fields:tuple=tuple()):
        self.repo = repo
        self.safe_fields = safe_fields + ('deleted',)

    def create_model(self, **kwargs)-> BaseModel:
        """
        Create an model object of the repository model.\n
        Applies business logic before creation\n
        Returns an model object.
        """
        return self.repo.model(**kwargs)
    
    def create_many(self, items:Iterable[dict[str,Any]])-> tuple[BaseModel]:
        """Try to create all the models in the iterable
            Raises RuntimeError if one fails"""
        try:
            models = tuple()
            for item in items:
                model = self.create_model(item)
                models += (model,)
            return models
        except:
            raise RuntimeError

    def add_model(self, model:BaseModel, commit:bool=True)-> BaseModel:
        return self.repo.add(model, commit=commit).to_dict(self.safe_fields)

    def add_new_model(self, commit:bool=True, **kwargs)-> BaseModel:
        return self.add_model(self.create_model(**kwargs),commit=commit)
    
    def add_many(self, models:Iterable[BaseModel], commit:bool=True)-> tuple[int]:
        """Try to add all the models in the iterable
            Rollback all if one fail
            Returns a tuple with all the models id"""
        try:
            inserted_ids = tuple()
            for model in models:
                model = self.repo.add(model, commit=commit)
                inserted_ids += (model.id,)
        except:
            self.repo.rollback()
            raise ValueError
        if commit:
            self.repo.commit()
        return inserted_ids
        
    def add_many_new(self,items:Iterable[dict[str,Any]], commit:bool=True, **kwargs)-> tuple[int]:
        """Try to create and add all the models in the iterable
            Rollback all if one fail
            Returns a tuple with all the models id"""
        return self.add_many(self.create_many(items=items, **kwargs),commit=commit)
            
    def delete_model(self, id)-> BaseModel:
        model = self.repo.get_by_id(id)
        return self.repo.delete(model).to_dict(self.safe_fields)

    def get_by_id(self, id:int)-> dict:
        return self.repo.get_by_id(id).to_dict(self.safe_fields)
    
    def get_by_filter(self, **kwargs)-> dict:
        values = self.repo.get_by_filter(**kwargs)
        serialized = []
        for value in values:
            serialized.append(value.to_dict(only=self.safe_fields))
        return serialized

    def commit(self):
        return self.repo.commit()
    
    def rollback(self):
        return self.repo.rollback()