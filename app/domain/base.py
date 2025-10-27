from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing import Optional
from sqlalchemy_serializer import SerializerMixin

class BaseModel(DeclarativeBase, SerializerMixin):
    # Control fields
    created_at: Mapped[Optional[datetime]] = mapped_column(default=func.now())
    last_update: Mapped[Optional[datetime]] = mapped_column(default=func.now(), onupdate=func.now())