from .base_service import BaseService
from repository.group_repository import GroupRepo
from domain.base import BaseModel
from typing import Iterable, Any

class GroupService(BaseService):
    def __init__(self):
        super().__init__(repo=GroupRepo(),
                         safe_fields=('id','creator_id','name','description',))
