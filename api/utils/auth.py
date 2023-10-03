import logging

from fastapi import HTTPException
from starlette import status
from starlette.requests import Request

from models.auth import Auth
from service.bucket_service import is_owner
from service.eth_service import verify_signature


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


async def extract_aws_token(request: Request) -> Auth | None:
    token = None
    auth_header = request.headers.get("Authorization") or request.headers.get("authorization")
    if auth_header:
        token = extract_token_from_aws_v4_auth_header(auth_header)
    if not token:
        token = request.headers.get("x-amz-security-token") or request.headers.get("X-Amz-Security-Token")
    if not token:
        token = request.headers.get("x-amz-token") or request.headers.get("X-Amz-Token")
    if not token:
        token = None

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")

    try:
        batch_id, signature = token.split("/")
        result, owner_address = await verify_signature(signature, batch_id)
    except Exception as e:
        logging.error(f"error while extracting auth {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid signature")

    if not result:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid signature")

    if not await is_owner(owner_address=owner_address, batch_id=batch_id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="address is not the batch owner")

    return Auth(batch_id=batch_id, owner_address=owner_address)


def extract_token(request: Request):
    token = extract_aws_token(request)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    return token
