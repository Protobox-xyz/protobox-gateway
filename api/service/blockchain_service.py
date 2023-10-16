from web3 import Web3
from settings import RPC_URL, BEE_PRIVATE_KEY
import logging

WEB3 = Web3(Web3.HTTPProvider(RPC_URL))


async def sign_transaction(call_function):
    # Sign transaction
    signed_tx = WEB3.eth.account.sign_transaction(call_function, private_key=BEE_PRIVATE_KEY)

    # Send transaction
    send_tx = WEB3.eth.send_raw_transaction(signed_tx.rawTransaction)

    # Wait for transaction receipt
    tx_receipt = WEB3.eth.wait_for_transaction_receipt(send_tx)

    logging.info(f"logging transaction receipt {tx_receipt}")
