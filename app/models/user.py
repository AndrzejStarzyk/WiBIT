from datetime import datetime
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from typing import Optional
from flask_login import UserMixin

from models.objectid import PydanticObjectId


class User(UserMixin, BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    user_id: int
    login: str
    password: Optional[str]
    date_added: Optional[datetime] = datetime.utcnow()
    date_updated: Optional[datetime] = datetime.utcnow()

    def to_json(self):
        return jsonable_encoder(self, exclude_none=True)

    def to_bson(self):
        data = self.dict(by_alias=True, exclude_none=True)
        if data.get("_id") is None:
            data.pop("_id", None)
        return data
