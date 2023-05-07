import base64
import json
import os

from elasticsearch import Elasticsearch
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

# define your Elasticsearch connection here
hostname = os.environ.get("ELASTIC_HOSTNAME", "http://notapixel.ddns.net:9200")
user = os.environ.get("ELASTIC_USERNAME", "godot")
password = os.environ.get("ELASTIC_PASSWORD", "cicciputte")
token = os.environ.get("TOKEN", "Godotexport_v1.0.0")

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
async def create_event(
    message: Message, request: Request, auth: str = Header(None, alias="Authorization")
):
    """
    Indexes a message in Elasticsearch and saves the message data to a JSON file.

    Args:
        message (Message): A Pydantic model representing the message to index.
            Must have fields 'id' and 'message'.

    Returns:
        dict: A JSON object with a message indicating whether the message
            has been indexed successfully or if an error occurred.

    Raises:
        Exception: If an error occurs while indexing the message in Elasticsearch.

    Example Usage:
        >>> message = {"id": "godot_1", "message": "alakamza"}
        >>> create_event(message)
        {"message": "Message has been indexed successfully."}
    """
    print("request arrived {}".format(request.headers.get("user-agent")))
    print(request.client.host)
    if not auth or not auth.startswith("Basic "):
        return JSONResponse(
            {"message": "Authorization header is missing or invalid"}, status_code=401
        )
        raise ValueError("Authorization header is missing or invalid")

    auth_token = auth.split(" ")[1]
    decoded_auth = base64.b64decode(auth_token.encode("utf-8")).decode("utf-8")
    print(decoded_auth)
    if "Godotexport_v1.0.0" not in decoded_auth:
        raise HTTPException(status_code=401, detail=f"Invalid authentication token {decoded_auth}")

    # dump json into file with name message.id
    with open("data/{}.json".format(message.id), "w") as f:
        f.write(json.dumps(message.dict()))
    print("message wrote to file with name {}.json".format(message.id))

    try:
        es.index(
            index="starship_olympics_analytics",  # id=message.id,
            document=message.dict(),
            op_type="create",
        )
    except Exception as e:
        print("Error: {}".format(e))
        return JSONResponse(
            {"message": "Could not index message properly because Error: {}".format(e)},
            status_code=502,
        )

    return {"message": "Message has been indexed successfully."}
