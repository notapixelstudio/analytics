from fastapi import FastAPI
from elasticsearch import Elasticsearch
from pydantic import BaseModel
import os

app = FastAPI()

# define your Elasticsearch connection here
hostname = os.environ.get('ELASTIC_HOSTNAME')
# get environment variable HOSTNAME
es = Elasticsearch(['http://localhost:9200'], timeout=30, max_retries=10, retry_on_timeout=True, username=os.environ.get("ELASTIC_USERNAME"), password=os.environ.get("ELASTIC_PASSWORD"))

# define your JSON schema here
class Message(BaseModel):
    id: str
    message: str

# define your API endpoint here
@app.post("/messages")
async def create_message(message: Message):
    es.index(index='starship_olympics_analytics', id=message.id, body=message.dict())
    return {"message": "Message has been indexed successfully."}