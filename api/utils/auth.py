from fastapi import HTTPException
from starlette import status
from starlette.requests import Request


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


def extract_aws_token(request: Request) -> str | None:
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
    return token


def extract_token(request: Request):
    token = extract_aws_token(request)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    return token
