from fastapi import FastAPI
from elasticsearch import Elasticsearch
from pydantic import BaseModel
import os

app = FastAPI()

# define your Elasticsearch connection here
hostname = os.environ.get('ELASTIC_HOSTNAME')
user = os.environ.get("ELASTIC_USERNAME")
password = os.environ.get("ELASTIC_PASSWORD")
# get environment variable HOSTNAME
es = Elasticsearch([hostname], verify_certs=False , timeout=30, max_retries=10, retry_on_timeout=True, 
                   basic_auth=[user, password])

# define your JSON schema here
class Message(BaseModel, extra="allow"):
    id: str
    message: str

# define your API endpoint here
@app.post("/messages")
async def create_message(message: Message):
    es.index(index='starship_olympics_analytics', #id=message.id,
              body=message.dict(), op_type='create')
    return {"message": "Message has been indexed successfully."}