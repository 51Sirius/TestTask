from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from bson import ObjectId
from typing import List
from motor.motor_asyncio import AsyncIOMotorClient
import aioredis

app = FastAPI()


class PydanticObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)


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
