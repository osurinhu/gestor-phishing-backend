from .base_service import BaseService
from repository.target_repository import TargetRepo
from domain.base import BaseModel
from typing import Iterable, Any

class TargetService(BaseService):
    def __init__(self):
        super().__init__(repo=TargetRepo(),
                         safe_fields=('id','creator_id','name','email','group_id',))
