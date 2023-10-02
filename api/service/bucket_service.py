from datetime import datetime
from starlette.requests import Request
from swarm_sdk.sdk import SwarmClient
from settings import MONGODB, SWARM_SERVER_URL


async def create_bucket(
    bucket: str,
    key: str,
    request: Request,
    owner: str,
):
    content_type = request.headers.get("Content-Type")
    swarm_client = SwarmClient(batch_id=owner, server_url=SWARM_SERVER_URL)
    swarm_upload_data = await swarm_client.upload(request.stream(), content_type=content_type, name=key)
    swarm_upload_data["SwarmServerUrl"] = SWARM_SERVER_URL

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
