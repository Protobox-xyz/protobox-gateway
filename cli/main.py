from pathlib import Path
import asyncio
import argparse

import boto3
import os

import botocore

ENDPOINT_URL = "http://localhost:8000/"
BATCH_ID = "b00b92417dd7d5c379dba70afd4f986675e05df2635beab6ff2a6eb6eb8b2208"


async def extract_token():
    with open(f"{Path.home()}/.protobox/authorization.txt", "r") as file:
        token = file.read()
        return token


async def get_client():
    token = await extract_token()
    session = boto3.session.Session()

    return session.client(
        "s3",
        endpoint_url=ENDPOINT_URL,
        aws_session_token=token,
        aws_secret_access_key=token,
        aws_access_key_id=token,
    )


async def handle_authorize(batch_id: str, signature: str):
    token = f"{batch_id}/{signature}"
    Path(f"{Path.home()}/.protobox").mkdir(parents=True, exist_ok=True)
    with open(f"{Path.home()}/.protobox/authorization.txt", "w") as file:
        file.write(token)

    print(f"Credentials was saved in {Path.home()}/.protobox")


async def handle_bucket_ls(bucket_name: str):
    client = await get_client()

    try:
        print(client.list_objects(Bucket=bucket_name))
    except botocore.exceptions.ClientError as e:
        print(e)


async def handle_download_object(bucket_name: str, key: str, dst_folder: str):
    client = await get_client()
    try:
        data = client.get_object(Bucket=bucket_name, Key=key)
    except botocore.exceptions.ClientError as e:
        print(e)

    file_path = os.path.join(dst_folder, key)
    # Get the directory of the file
    directory = os.path.dirname(file_path)
    Path(directory).mkdir(parents=True, exist_ok=True)
    with open(file_path, "wb") as file:
        file.write(data["Body"].read())


async def handle_upload_folder(path: str, bucket_name: str):
    client = await get_client()
    for root, dirs, file in os.walk(path):
        for f in file:
            key = os.path.relpath(os.path.join(root, f), start=path)
            file_path = os.path.abspath(os.path.join(root, f))
            with open(file_path, "rb") as file:
                bytes_data = file.read()
                try:
                    client.put_object(Bucket=bucket_name, Key=key, Body=bytes_data)
                except botocore.exceptions.ClientError as e:
                    print(e)


async def main():
    """
    Command line parser that acts on the command passed to it
    """
    parser = argparse.ArgumentParser(description="Command line tool for Protobox")
    subparses = parser.add_subparsers()

    # keys generation functionality
    ls = subparses.add_parser("ls", help="create n validator keys")
    ls.add_argument("-b", "--bucket", help="bucket name of your user", required=True)
    ls.set_defaults(which="ls")

    # download file
    download = subparses.add_parser("download", help="download the uploaded file")
    download.add_argument("-b", "--bucket", help="bucket name of your user", required=True)
    download.add_argument("-k", "--key", help="key of the object", required=True)
    download.add_argument("-dst", "--destination", help="destination folder", default="")
    download.set_defaults(which="download")

    # upload the directory
    upload_folder = subparses.add_parser("upload_folder", help="upload the directory or file in bucket")
    upload_folder.add_argument("-b", "--bucket", help="bucket name of your user", required=True)
    upload_folder.add_argument("-dir", "--directory", help="local folder or file path", default="")
    upload_folder.set_defaults(which="upload_folder")

    # authorize command
    authorize = subparses.add_parser("authorize", help="authorize command")
    authorize.add_argument("-b", "--batch", help="batch id of the swarm", required=True)
    authorize.add_argument(
        "-sig", "--signature", help="specific signature generated to authorize on protobox", required=True
    )
    authorize.set_defaults(which="authorize")

    args = parser.parse_args()
    if args.which == "ls":
        await handle_bucket_ls(bucket_name=args.bucket)
    elif args.which == "download":
        await handle_download_object(bucket_name=args.bucket, key=args.key, dst_folder=args.destination)
    elif args.which == "upload_folder":
        await handle_upload_folder(bucket_name=args.bucket, path=args.directory)
    elif args.which == "authorize":
        await handle_authorize(batch_id=args.batch, signature=args.signature)


if __name__ == "__main__":
    asyncio.run(main())
