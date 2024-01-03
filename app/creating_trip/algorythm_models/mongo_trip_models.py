from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List

from models.objectid import PydanticObjectId


class ScheduleMongo(BaseModel):
    date: str
    start: datetime
    end: datetime


class PoiMongo(BaseModel):
    poi_id: str
    plan_from: datetime
    plan_to: datetime


class DayMongo(BaseModel):
    schedule: ScheduleMongo
    trajectory: List[PoiMongo]


class TripDaysMongo(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    user_id: PydanticObjectId
    days: List[DayMongo]
    region: str

    def to_bson(self):
        data = self.dict(by_alias=True, exclude_none=True)
        if data.get("_id") is None:
            data.pop("_id", None)
        return data






