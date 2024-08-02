import json
from typing import List
from motor.motor_asyncio import AsyncIOMotorClient
import aioredis
from typing import Annotated, Any, Callable

from bson import ObjectId
from fastapi import FastAPI
from pydantic import BaseModel, Field, GetJsonSchemaHandler
from pydantic_core import core_schema

app = FastAPI()


class _ObjectIdPydanticAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(
            cls,
            _source_type: Any,
            _handler: Callable[[Any], core_schema.CoreSchema],
    ) -> core_schema.CoreSchema:
        def validate_from_str(input_value: str) -> ObjectId:
            return ObjectId(input_value)

        return core_schema.union_schema(
            [
                core_schema.is_instance_schema(ObjectId),
                core_schema.no_info_plain_validator_function(validate_from_str),
            ],
            serialization=core_schema.to_string_ser_schema(),
        )


PydanticObjectId = Annotated[
    ObjectId, _ObjectIdPydanticAnnotation
]


class Message(BaseModel):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    user: str
    content: str


class MessageCreate(BaseModel):
    user: str
    content: str


client = AsyncIOMotorClient("mongodb://mongo:27017")
db = client["message_db"]
redis = None


@app.on_event("startup")
async def startup():
    global redis
    redis = aioredis.from_url("redis://redis")


@app.on_event("shutdown")
async def shutdown():
    await redis.close()


@app.get("/api/v1/messages/", response_model=List[Message])
async def get_messages():
    messages = await redis.get("messages")
    if messages:
        return json.loads(messages)
    messages = await db["messages"].find().to_list(1000)
    await redis.set("messages", json.dumps(messages, default=str))
    return messages


@app.post("/api/v1/message/")
async def create_message(message: MessageCreate):
    message_dict = message.dict()
    result = await db["messages"].insert_one(message_dict)
    message_dict["_id"] = str(result.inserted_id)
    await redis.delete("messages")
    return message_dict
