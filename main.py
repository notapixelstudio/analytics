import json
import os

from elasticsearch import Elasticsearch
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# define your Elasticsearch connection here
hostname = os.environ.get("ELASTIC_HOSTNAME")
user = os.environ.get("ELASTIC_USERNAME")
password = os.environ.get("ELASTIC_PASSWORD")

print("{}:{}@{}".format(user, password, hostname))

# get environment variable HOSTNAME
es = Elasticsearch(
    [hostname],
    verify_certs=False,
    timeout=30,
    max_retries=10,
    retry_on_timeout=True,
    basic_auth=[user, password],
)


# define your JSON schema here
class Message(BaseModel, extra="allow"):
    id: str
    message: str


# define your API endpoint here
@app.post("/messages")
async def create_event(message: Message):
    try:
        es.index(
            index="starship_olympics_analytics",  # id=message.id,
            document=message.dict(),
            op_type="create",
        )
    except Exception as e:
        return {"message": "Error: {}".format(e)}
    # dump json into file with name message.id
    with open("{}.json".format(message.id), "w") as f:
        f.write(json.dumps(message.dict()))

    return {"message": "Message has been indexed successfully."}
