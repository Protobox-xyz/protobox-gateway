from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException
from starlette import status
from starlette.requests import Request

from models.data_transfer import Action
from swarm_sdk.sdk import SwarmClient
from settings import MONGODB, SWARM_SERVER_URL_BZZ
import logging


async def create_bucket(bucket: str, key: str, request: Request, owner: str, application: str):
    content_type = request.headers.get("Content-Type")
    content_length = int(request.headers.get("content-length", 0))

    swarm_client = SwarmClient(batch_id=owner, server_url=SWARM_SERVER_URL_BZZ)
    swarm_upload_data, status_code = await swarm_client.upload(request.stream(), content_type=content_type, name=key)
    swarm_upload_data["SwarmServerUrl"] = SWARM_SERVER_URL_BZZ
    print(swarm_upload_data, status_code)

    if status_code >= 300:
        raise HTTPException(status_code=status_code, detail=swarm_upload_data["message"])

    MONGODB.objects.replace_one(
        {"_id": {"Bucket": bucket, "Key": key}},
        {
            "_id": {"Bucket": bucket, "Key": key},
            "Bucket": bucket,
            "Key": key,
            "Owner": owner,
            "CreationDate": datetime.now(),
            "SwarmData": swarm_upload_data,
            "content_type": content_type,
            "content_length": content_length,
            "application": application,
        },
        upsert=True,
    )

    now = datetime.utcnow()
    MONGODB.data_transfer.insert_one(
        {
            "_id": uuid4().hex,
            "action": Action.UPLOAD,
            "batch_id": owner,
            "application": application,
            "bucket_id": bucket,
            "content_length": content_length,
            "content_type": content_type,
            "key": key,
            "updated_at": now,
            "created_at": now,
        }
    )


async def save_download_transfer(data, bucket_id: str, application: str, key: str, batch_id: str):
    logging.info("Saving download data transfer")
    now = datetime.utcnow()
    MONGODB.data_transfer.insert_one(
        {
            "_id": uuid4().hex,
            "action": Action.DOWNLOAD,
            "application": application,
            "batch_id": batch_id,
            "bucket_id": bucket_id,
            "content_length": int(data["content_length"]),
            "content_type": data["content_type"],
            "key": key,
            "updated_at": now,
            "created_at": now,
        }
    )


async def filter_prefixes(prefix: str, objects: list):
    if prefix != "" and not prefix.endswith("/"):
        prefix += "/"

    result = []
    used_folder = {}
    for obj in objects:
        key = obj["Key"]
        if key == prefix[:-1]:
            obj["Folder"] = False
            result.append(obj)
            continue
        # get child of this prefix
        children = key[len(prefix) :]

        children = children.split("/")
        if len(children) < 1:
            continue
        child = prefix + children[0]
        if child in used_folder:
            continue

        result.append(
            {
                "Bucket": obj["Bucket"],
                "Key": child,
                "Owner": obj["Owner"],
                "Name": children[0],
                "Folder": len(children) > 1,
                "CreationDate": obj["CreationDate"],
                "content_length": obj["content_length"],
                "content_type": obj["content_type"],
            }
        )
        used_folder[child] = True

    return result


async def get_owner_objects(bucket_id, owner_address, prefix=""):
    bucket_info = MONGODB.buckets.find_one({"_id": bucket_id})

    if not bucket_info or not await is_owner(owner_address, bucket_info["Owner"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="invalid bucket owner")

    query = {"Bucket": bucket_id}
    if prefix != "":
        query["Key"] = {"$regex": f"^{prefix}"}

    objects = list(MONGODB.objects.find(query, {"_id": 0, "Content": 0}))
    print(objects)
    return await filter_prefixes(prefix, objects)


async def get_owner_objects_s3(bucket, batch_id: str, skip: int, limit: int, prefix=""):
    bucket_info = MONGODB.buckets.find_one({"Name": bucket, "Owner": batch_id})
    if not bucket_info:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="invalid bucket owner")

    query = {"Bucket": bucket_info["_id"]}
    if prefix != "":
        query["Key"] = {"$regex": f"^{prefix}"}

    objects = list(MONGODB.objects.find(query, {"_id": 0, "Content": 0}, skip=skip, limit=limit))
    return objects


def get_owner_data(owner):
    return {"ID": owner, "DisplayName": owner}


def get_owner_buckets(owner):
    yield from MONGODB.buckets.find({"Owner": owner})


async def get_user_buckets(account_address):
    batches = MONGODB.batches.find({"owner": account_address})
    buckets = []
    for batch in batches:
        buckets += list(MONGODB.buckets.find({"Owner": batch["batch_id"]}))
    return buckets


async def is_owner(owner_address: str, batch_id: str):
    batch = MONGODB.batches.find_one({"owner": owner_address, "batch_id": batch_id})
    return False if not batch else True


async def get_object_data(bucket_id: str, key: str, owner_address: str):
    data = MONGODB.objects.find_one({"_id": {"Bucket": bucket_id, "Key": key}})

    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bucket Not Found")

    if not await is_owner(owner_address, data["Owner"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="invalid batch owner")

    return data
