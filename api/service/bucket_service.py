import logging
from datetime import datetime
from starlette.requests import Request
from swarm_sdk.sdk import SwarmClient
from settings import MONGODB, SWARM_SERVER_URL_BZZ, SWARM_SERVER_URL_STAMP
from hexbytes import HexBytes
from eth_account.messages import encode_defunct
from web3 import Web3
from fastapi import HTTPException

from models.batches_router import BatchResponse

WEB3 = Web3()


async def create_bucket(
    bucket: str,
    key: str,
    request: Request,
    owner: str,
):
    content_type = request.headers.get("Content-Type")
    swarm_client = SwarmClient(batch_id=owner, server_url=SWARM_SERVER_URL_BZZ)
    swarm_upload_data = await swarm_client.upload(request.stream(), content_type=content_type, name=key)
    swarm_upload_data["SwarmServerUrl"] = SWARM_SERVER_URL_BZZ

    print(swarm_upload_data)

    MONGODB.objects.replace_one(
        {"_id": {"Bucket": bucket, "Key": key}},
        {
            "_id": {"Bucket": bucket, "Key": key},
            "Bucket": bucket,
            "Key": key,
            "Owner": owner,
            "CreationDate": datetime.now(),
            "SwarmData": swarm_upload_data,
        },
        upsert=True,
    )


def get_owner_objects(bucket, owner, prefix=None, limit=1000, skip=0):
    query = {"Owner": owner, "Bucket": bucket}
    skip = skip or 0
    limit = 1000 if limit is None else limit
    if prefix:
        query["Key"] = {"$regex": f"^{prefix}"}
    yield from MONGODB.objects.find(query, {"_id": 0, "Content": 0}).skip(skip).limit(limit)


def get_owner_data(owner):
    return {"ID": owner, "DisplayName": owner}


def get_owner_buckets(owner):
    yield from MONGODB.buckets.find({"Owner": owner})


def verify_signature(signature: str) -> (bool, str):
    if signature is None:
        return False, None
    try:
        encoded_message = encode_defunct(text="create batch")
        address = WEB3.eth.account.recover_message(encoded_message, signature=HexBytes(signature))
    except Exception as e:
        logging.error(e)
        return False, None
    return True, address


async def create_batch(signature: str):
    verify, owner = verify_signature(signature)

    logging.info(f"creating batch with owner {owner}")

    if not verify:
        raise HTTPException(status_code=400, detail="invalid signature")

    amount = 100000000
    depth = 20

    swarm_client = SwarmClient(batch_id=owner, server_url=SWARM_SERVER_URL_STAMP)
    swarm_upload_data = await swarm_client.create_batch(amount=amount, depth=depth)

    logging.info(f"created swarm batch id {swarm_upload_data}")

    batch_id = swarm_upload_data["batchID"]

    MONGODB.batches.insert_one({"_id": batch_id, "owner": owner, "batch_id": batch_id})

    return BatchResponse(batch_id=batch_id, owner=owner, _id=batch_id)
