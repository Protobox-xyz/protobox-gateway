import logging

from fastapi import HTTPException
from starlette import status

from models.batches_router import BatchResponse
from settings import SWARM_SERVER_URL_STAMP, MONGODB, ERC20_ABI, BZZ_COIN_ADDRESS
from swarm_sdk.sdk import SwarmClient
from service.blockchain_service import WEB3, sign_transaction

bzz_contract = WEB3.eth.contract(address=BZZ_COIN_ADDRESS, abi=ERC20_ABI)


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
    except Exception as e:
        logging.error(f"error while transferring error message: {e}")
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="cant transfer money from owner's account"
        )


async def create_batch(owner: str, amount: int, label: str):
    # in future this two var should be changed
    depth = 20
    await transfer_from_bzz_coins(owner_address=owner, amount=amount)

    swarm_client = SwarmClient(batch_id=owner, server_url=SWARM_SERVER_URL_STAMP)
    swarm_response, status_code = await swarm_client.create_batch(amount=amount, depth=depth, label=label)

    if 400 <= status_code:
        raise HTTPException(status_code=status_code, detail=swarm_response)

    logging.info(f"created swarm batch id {swarm_response}")

    batch_id = swarm_response["batchID"]

    MONGODB.batches.insert_one({"_id": batch_id, "owner": owner, "batch_id": batch_id})

    return BatchResponse(batch_id=batch_id, owner=owner, _id=batch_id, info=await get_batch_info(batch_id))


async def get_batch_info(batch_id):
    swarm_client = SwarmClient(batch_id=batch_id, server_url=SWARM_SERVER_URL_STAMP)
    return await swarm_client.get_batch_info(batch_id)


async def get_owner_batches(owner):
    logging.info(f"getting batches {owner}")
    batches = list(MONGODB.batches.find({"owner": owner}))
    for batch in batches:
        batch["info"] = await get_batch_info(batch["batch_id"])
    return batches
