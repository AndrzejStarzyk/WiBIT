from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List

from models.objectid import PydanticObjectId


class TextPreferences(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    user_id: PydanticObjectId
    preferences_text: str
    date_text: str

    def to_bson(self):
        data = self.dict(by_alias=True, exclude_none=True)
        if data.get("_id") is None:
            data.pop("_id", None)
        return data
