import logging

from fastapi import HTTPException, Header
from starlette import status
from starlette.requests import Request

from models.auth import Auth
from service.bucket_service import is_owner
from service.eth_service import verify_signature
from settings import SING_IN_MESSAGE


def extract_token_from_aws_v4_auth_header(auth_header: str) -> str | None:
    auth_header_parts = auth_header.split()
    if len(auth_header_parts) < 2:
        return None
    if auth_header_parts[0] != "AWS4-HMAC-SHA256":
        return None
    credential_parts = auth_header_parts[1]
    if not credential_parts.startswith("Credential="):
        return None
    credential_parts = credential_parts[11:]
    return credential_parts.split("/")[0]


async def extract_aws_token(
    request: Request,
    x_amz_security_token: str = Header(None),
    authorization: str = Header(None),
    x_amz_token: str = Header(None),
) -> Auth | None:
    token = None

    if x_amz_token:
        token = token
    elif x_amz_security_token:
        token = x_amz_security_token
    elif authorization:
        token = authorization
    else:
        token = extract_token_from_aws_v4_auth_header

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")

    try:
        batch_id, signature, application = token.split("/")
        result, owner_address = await verify_signature(signature, SING_IN_MESSAGE)
    except Exception as e:
        logging.error(f"error while extracting auth {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid signature")

    if not result:
        logging.error(f"error in signature")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid signature")

    if not await is_owner(owner_address=owner_address, batch_id=batch_id):
        logging.error(f"invalid owner")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="address is not the batch owner")

    return Auth(batch_id=batch_id, owner_address=owner_address, application=application)


async def extract_token(request: Request):
    batch_id = request.headers.get("batch-id")

    if not batch_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing batch id")

    owner_address = await extract_signature(request=request)

    if not await is_owner(owner_address=owner_address, batch_id=batch_id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="address is not the batch owner")

    return Auth(batch_id=batch_id, owner_address=owner_address)


async def extract_signature(request: Request):
    signature = request.headers.get("signature")

    if not signature:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")

    try:
        result, owner_address = await verify_signature(signature, SING_IN_MESSAGE)
    except Exception as e:
        logging.error(f"error while extracting auth {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid signature")

    if not result:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid signature")

    return owner_address
