from datetime import datetime
import logging

from models.batches_router import BatchRequest, BatchExtendRequest
from settings import SWARM_SERVER_URL_STAMP, MONGODB, ERC20_ABI, BZZ_COIN_ADDRESS
from swarm_sdk.sdk import SwarmClient
from service.blockchain_service import WEB3, sign_transaction

bzz_contract = WEB3.eth.contract(address=WEB3.to_checksum_address(BZZ_COIN_ADDRESS), abi=ERC20_ABI)


async def get_bee_ethereum_address():
    swarm_client = SwarmClient(batch_id="", server_url=SWARM_SERVER_URL_STAMP)
    addresses = await swarm_client.get_addresses()
    return WEB3.to_checksum_address(addresses["ethereum"])


async def transfer_from_bzz_coins(owner_address: str, amount: int):
    bee_ethereum_address = await get_bee_ethereum_address()

    # Initialize address nonce
    try:
        nonce = WEB3.eth.get_transaction_count(bee_ethereum_address)

        call_function = bzz_contract.functions.transferFrom(
            owner_address, bee_ethereum_address, amount
        ).build_transaction(
            {
                "from": bee_ethereum_address,
                "nonce": nonce,
            }
        )

        await sign_transaction(call_function=call_function)

        logging.info(f"transferring from {owner_address} to {bee_ethereum_address} amount: {amount}")
        return True
    except Exception as e:
        logging.error(f"error while transferring error message: {e}")
        return False


async def create_batch_task(task_id: str, owner: str, batch: BatchRequest):
    success = await transfer_from_bzz_coins(owner_address=owner, amount=batch.amount)

    if not success:
        MONGODB.tasks.replace_one({"_id": task_id}, {"finished": True, "status_code": 402, "response": {}})
        return

    swarm_client = SwarmClient(batch_id=owner, server_url=SWARM_SERVER_URL_STAMP)

    plur = batch.amount // 2**batch.depth
    swarm_response, status_code = await swarm_client.create_batch(amount=plur, depth=batch.depth, label=batch.label)

    logging.info(f"post request on endpoint: {SWARM_SERVER_URL_STAMP}")

    if 400 <= status_code:
        logging.error(f"error while creating batch: {swarm_response} amount: {plur} depth: {batch.depth}")
        MONGODB.tasks.replace_one(
            {"_id": task_id}, {"finished": True, "status_code": status_code, "response": swarm_response}
        )
        return

    logging.info(f"created swarm batch id {swarm_response}")

    batch_id = swarm_response["batchID"]

    now = datetime.utcnow()
    MONGODB.batches.insert_one(
        {"_id": batch_id, "owner": owner, "batch_id": batch_id, "created_at": now, "updated_at": now}
    )

    MONGODB.tasks.replace_one(
        {"_id": task_id},
        {
            "finished": True,
            "status_code": status_code,
            "response": {"batch_id": batch_id, "owner": owner, "_id": batch_id},
        },
    )


async def extend_batch_task(task_id: str, batch_id: str, owner: str, batch: BatchExtendRequest):
    success = await transfer_from_bzz_coins(owner_address=owner, amount=batch.amount)

    if not success:
        MONGODB.tasks.replace_one({"_id": task_id}, {"finished": True, "status_code": 402, "response": {}})
        return

    plur = batch.amount // 2**batch.depth

    swarm_client = SwarmClient(batch_id=owner, server_url=SWARM_SERVER_URL_STAMP)
    swarm_response, status_code = await swarm_client.extend_batch(batch_id=batch_id, amount=plur)

    if 400 <= status_code:
        logging.error(f"error while creating batch: {swarm_response}")
        MONGODB.tasks.replace_one(
            {"_id": task_id}, {"finished": True, "status_code": status_code, "response": swarm_response}
        )
        return

    logging.info(f"created swarm batch id {swarm_response}")

    now = datetime.utcnow()
    MONGODB.batches.update_one({"_id": batch_id}, {"$set": {"updated_at": now}})

    MONGODB.tasks.replace_one(
        {"_id": task_id},
        {
            "finished": True,
            "status_code": status_code,
            "response": {"batch_id": batch_id, "owner": owner, "_id": batch_id},
        },
    )


async def get_batch_info(batch_id):
    swarm_client = SwarmClient(batch_id=batch_id, server_url=SWARM_SERVER_URL_STAMP)
    batch, status = await swarm_client.get_batch_info(batch_id)
    if status != 200:
        return {
            "utilization": 0,
            "usable": False,
            "label": "asd",
            "depth": 0,
            "amount": 0,
            "bucketDepth": 0,
            "blockNumber": 0,
            "immutableFlag": True,
            "exists": False,
            "batchTTL": 0,
        }

    return batch


async def get_owner_batches(owner):
    logging.info(f"getting batches {owner}")
    batches = list(MONGODB.batches.find({"owner": owner}).sort("created_at"))
    for batch in batches:
        batch["info"] = await get_batch_info(batch["batch_id"])

    return batches
