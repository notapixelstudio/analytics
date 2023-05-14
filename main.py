import base64
import json
import logging
import os
from ipaddress import IPv4Address, ip_address
from typing import Optional

from elasticsearch import Elasticsearch
from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel

app = FastAPI(version="0.6.0", title="SO Analytics", description="SO Analytics API")

# define your Elasticsearch connection here
hostname = os.environ.get("ELASTIC_HOSTNAME", "https://localhost:9200")
user = os.environ.get("ELASTIC_USERNAME", "elastic")
password = os.environ.get("ELASTIC_PASSWORD", "changeme")
token = os.environ.get("TOKEN", "secret_token")

# Initialize logger
logger = logging.getLogger("api_logger")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


def validate_ip_address(ip: str) -> Optional[str]:
    try:
        return "IPv4" if type(ip_address(ip)) is IPv4Address else "IPv6"
    except ValueError:
        return None


def anonymize_ip(ip: str) -> str:
    ipv4_mask = int(ip_address("255.255.255.0"))
    ipv6_mask = int(ip_address("ffff:ffff:ffff:ffff::"))
    if validate_ip_address(ip) == "IPv4":
        return str(ip_address(int(ip_address(ip)) & ipv4_mask))
    if validate_ip_address(ip) == "IPv6":
        return str(ip_address(int(ip_address(ip)) & ipv6_mask))
    return None


# get environment variable HOSTNAME
es = Elasticsearch(
    [hostname],
    verify_certs=False,
    timeout=30,
    max_retries=10,
    retry_on_timeout=True,
    basic_auth=[user, password],
)
logger.info("Connected to Elasticsearch at %s", hostname)


class Event(BaseModel, extra="allow"):
    id: str
    version: str
    event_name: str


@app.post("/messages")
async def create_event(
    message: Event, request: Request, auth: str = Header(None, alias="Authorization")
):
    """
    Indexes a message in Elasticsearch and saves the message data to a JSON file.

    Args:
        message (Event): A Pydantic model representing the message to index.
            Must have fields 'id' and 'message' and 'version'.

    Returns:
        dict: A JSON object with a message indicating whether the message
            has been indexed successfully or if an error occurred.

    Raises:
        Exception: If an error occurs while indexing the message in Elasticsearch.
        HTTPException: If an authentication error occurs.

    Example Usage:
        >>> message = {"id": "godot_1", "message": "alakamza"}
        >>> create_event(message)
        {"message": "Message has been indexed successfully."}
    """
    logger.info(
        "Request received from client with user-agent %s", request.headers.get("user-agent")
    )
    logger.info("Request received from IP address %s", request.client.host)

    message.ip = anonymize_ip(request.client.host)
    message.user_agent = request.headers.get("user-agent")
    message.api_version = app.version

    if not auth or not auth.startswith("Basic "):
        raise HTTPException(status_code=401, detail="Authorization header is missing or invalid")

    auth_token = auth.split(" ")[1]
    decoded_auth = base64.b64decode(auth_token.encode("utf-8")).decode("utf-8")
    logger.info("Decoded authorization token: %s", decoded_auth)

    if "Godotexport_v1.0.0" not in decoded_auth:
        raise HTTPException(status_code=401, detail=f"Invalid authentication token {decoded_auth}")

    # Dump json into file with name message.id
    with open(f"data/{message.id}.json", "w") as f:
        f.write(json.dumps(message.dict()))

    logger.info("Event data saved to file with name %s.json", message.id)

    try:
        es.index(
            index="starship_olympics_analytics",
            document=message.dict(),
            op_type="create",
            pipeline="geoip",
        )
        logger.info(f"Event {message.event_name} has been indexed successfully.")
    except Exception as e:
        logger.error("Could not index message properly because of %s", str(e))
        raise HTTPException(
            status_code=502,
            detail=f"Could not index message properly because of {str(e)}",
        )

    return {
        "message": (
            f"Event {message.event_name} has been indexed successfully. API version: {app.version}"
        )
    }
