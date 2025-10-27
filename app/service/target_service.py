from .base_service import BaseService
from repository.target_repository import TargetRepo
from domain.base import BaseModel
from typing import Iterable, Any

class TargetService(BaseService):
    def __init__(self):
        super().__init__(repo=TargetRepo(),
                         safe_fields=('id','creator_id','name','email','group_id',))

    def create_many(self, group_id:int, creator_id:int, items:Iterable[dict[str,Any]])-> tuple[BaseModel]:
        """Try to create all the models in the iterable.
            Raises RuntimeError if one fails.\n
            :param items:\n
                Dictonary containing 'target_name' and 'target_email'.
            :param group_id:\n
                Id of the group to wich the target is part of.\n
            :param creator_id:\n
                Id of the user trying to create the target.\n"""
        try:
            models = tuple()
            for item in items:
                model = self.create_model(
                    group_id=group_id,
                    creator_id=creator_id,
                    name=item['target_name'],
                    email=item['target_email']
                )
                models += (model,)
            return models
        except:
            raise RuntimeError