import logging

from eth_account.messages import encode_defunct
from hexbytes import HexBytes

from web3 import Web3

WEB3 = Web3()


async def verify_signature(signature: str, message_text) -> (bool, str):
    if signature is None:
        return False, None
    try:
        encoded_message = encode_defunct(text=message_text)
        address = WEB3.eth.account.recover_message(encoded_message, signature=HexBytes(signature))
    except Exception as e:
        logging.error(e)
        return False, None
    return True, address
