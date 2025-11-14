from repository import base_repository
from domain.base import BaseModel
from typing import Iterable, Any

class BaseService:
    def __init__(self, repo: base_repository, user_id:int=None, have_ownership:bool=False, safe_fields:tuple=tuple()):
        if have_ownership and not user_id and user_id !=0:
            raise NotImplementedError

        self.repo = repo
        self.safe_fields = safe_fields
        self.have_ownership = have_ownership
        self.user_id = user_id

    def validate_ownership(self, model:BaseModel):
        if self.have_ownership and self.user_id != 0:
            if model.creator_id != self.user_id:
                raise PermissionError

    def before_create(self, kwargs):
        pass

    def create(self, commit:bool=True, **kwargs)-> dict:
        self.before_create(kwargs)
        return self.add_model(self.create_model(**kwargs),commit=commit)
    
    def create_many(self, items:Iterable[dict[str,Any]], commit:bool=True, **kwargs)-> tuple[int]:
        """Try to create and add all the models in the iterable
            Rollback all if one fail
            Returns a tuple with all the models id"""
        return self.add_many_models(self.create_many_models(items=items, **kwargs),commit=commit)

    def create_model(self, **kwargs)-> BaseModel:
        if self.have_ownership:
            kwargs['creator_id'] = self.user_id

        return self.repo.model(**kwargs)
    
    def create_many_models(self, items:Iterable[dict], **kwargs)-> tuple[BaseModel]:
        """Try to create all the models in the iterable.
            Raises RuntimeError if one fails.

            :param items: Individual values of each new model.
            :type items: Iterable[dict].
            :param kwargs: Values that every new model share.
            :returns: A tuple with every new object.
            :rtype: tuple[BaseModel]
            """
        try:
            models = tuple()
            for item in items:
                model = self.create_model(**item, **kwargs)
                models += (model,)
            return models
        except:
            raise RuntimeError

    def add_model(self, model:BaseModel, commit:bool=True)-> dict:
        model = self.repo.add(model)

        if commit:
            self.commit()

        return model.to_dict(self.safe_fields)
    
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
    
    def before_update(self, model:BaseModel, kwargs):
        pass

    def update(self, id:int, commit:bool=True, **kwargs):
        model = self.repo.get_by_id(id=id)
        if not model:
            raise PermissionError
        self.validate_ownership(model)
        self.before_update(model, kwargs)
        args = dict()
        for key, value in kwargs.items(): 
            if value:
                args[key] = value
        model = self.repo.update(model=model, **args)
        if commit:
            self.commit()
        return model.to_dict(self.safe_fields)
            
    def before_delete(self, model:BaseModel):
        pass
        
    def delete(self, id:int, commit:bool=True)-> dict:
        model = self.repo.get_by_id(id)
        if not model:
            raise PermissionError
        self.validate_ownership(model)
        self.before_delete(model)
        model =  self.repo.delete(model)
        if commit:
            self.commit()
        return model.to_dict(self.safe_fields)
    
    def before_put(self, new_entry:dict, old_model:BaseModel):
        pass

    def put(self, id, commit = True, **kwargs):
        old_model = self.repo.get_by_id(id)
        new_entry =  self.create(**kwargs, commit=False)
        self.before_put(new_entry, old_model)
        try:
            self.delete(id, commit=False)
        except:
            pass
        if commit:
            self.commit()
        return new_entry

    def get_by_id(self, id:int, fields:list=None, extra_fields:tuple=None, show_deleted:bool=False)-> dict:
        model = self.repo.get_by_id(id)
        if not model:
            return None

        try:
            self.validate_ownership(model)
        except PermissionError:
            return None

        if model.deleted and not show_deleted:
            return None
            
        if not fields:
            fields=self.safe_fields

        if extra_fields:
            fields += extra_fields


        return model.to_dict(fields)
    
    def get_by_filter(self, fields:tuple=None, extra_fields:tuple=None, limit:int=None, show_deleted:bool=False, **kwargs)-> dict:
        """Returns a list with the query elements"""
        if self.have_ownership and self.user_id != 0:
            kwargs['creator_id'] = self.user_id

        if not show_deleted:
            kwargs['deleted'] = False

        if not fields:
            fields=self.safe_fields
        
        if extra_fields:
            fields += extra_fields

        values = self.repo.get_by_filter(**kwargs, limit=limit)
        serialized = []
        for value in values:
            serialized.append(value.to_dict(fields))
        return serialized

    def get_page_filtered(self, fields:tuple=None, extra_fields:tuple=None, page:int=1, per_page:int=20, exact:dict=dict(), **kwargs)-> dict:
        """
            Get dict of a querys page.

            :param fields: Which filds of the model should be returned, overrides safe_fields.
            :type field: tuple[str]
            :param extra_fields: Which filds of the model should be returned, joins with safe_fields.
            :type extra_field: tuple[str]
            :param page: Which page should be returned.
            :type page: int
            :param per_page: Number of elements in the page.
            :type per_page: int
            :param exact: Key value pairs that represent exact matchs of model value 
            :type exact: dict
            :param kwargs: Arguments passed as not exact match of an model value
            :type kwargs: str
        """
        exact['deleted'] = False
        if self.have_ownership:
            exact['creator_id'] = self.user_id
        
        if not fields:
            fields=self.safe_fields

        if extra_fields:
            fields += extra_fields

        p = self.repo.get_page_by_filter(page=page, per_page=per_page, exact=exact, like=kwargs)

        items = []
        for item in p:
            items.append(item.to_dict(only=fields))
        return {
            'items': items,
            'current_page': p.page,
            'total_of_items': p.total,
            'total_of_pages': p.pages,
            'has_prev': p.has_prev,
            'has_next': p.has_next,
        }

    def exists(self, id)-> bool:
        if self.get_by_id(id=id):
            return True
        return False

    def commit(self):
        return self.repo.commit()
    
    def rollback(self):
        return self.repo.rollback()