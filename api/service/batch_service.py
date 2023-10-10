import logging

from models.batches_router import BatchResponse
from settings import SWARM_SERVER_URL_STAMP, MONGODB
from swarm_sdk.sdk import SwarmClient


async def create_batch(owner: str):
    # in future this two var should be changed
    amount = 100000000
    depth = 20

    swarm_client = SwarmClient(batch_id=owner, server_url=SWARM_SERVER_URL_STAMP)
    swarm_upload_data = await swarm_client.create_batch(amount=amount, depth=depth)

    logging.info(f"created swarm batch id {swarm_upload_data}")

    batch_id = swarm_upload_data["batchID"]

    MONGODB.batches.insert_one({"_id": batch_id, "owner": owner, "batch_id": batch_id})

    return BatchResponse(batch_id=batch_id, owner=owner, _id=batch_id)


async def get_batch_info(batch_id):
    swarm_client = SwarmClient(batch_id=batch_id, server_url=SWARM_SERVER_URL_STAMP)
    return await swarm_client.get_batch_info(batch_id)


async def get_owner_batches(owner):
    logging.info(f"getting batches {owner}")
    batches = list(MONGODB.batches.find({"owner": owner}))
    for batch in batches:
        batch["info"] = await get_batch_info(batch["batch_id"])
    return batches
