from pathlib import Path
import asyncio
import argparse

import boto3
import os

ENDPOINT_URL = "http://localhost:8000/"
BATCH_ID = "b00b92417dd7d5c379dba70afd4f986675e05df2635beab6ff2a6eb6eb8b2208"
TOKEN = "258f929b1fa671db4009fe18646fce39e4a811f0f58bb4557e21121cc3d7f3a5/0x18a22dc629c07c02cbba3942ce3b977db76d23bc08e722eb6be42a5b6d6d7a8d02e271a6e88895a8662d5339d33efc8ca442299a01e5b5becc3145b5f01eea5c1c"


# test123
async def get_client():
    session = boto3.session.Session()

    return session.client(
        "s3",
        endpoint_url=ENDPOINT_URL,
        aws_session_token=TOKEN,
        aws_secret_access_key=TOKEN,
        aws_access_key_id=TOKEN,
    )


async def handle_bucket_ls(bucket_name: str):
    client = await get_client()
    print(client.list_objects(Bucket=bucket_name))


async def handle_download_object(bucket_name: str, key: str, dst_folder: str):
    client = await get_client()
    data = client.get_object(Bucket=bucket_name, Key=key)
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
                client.put_object(Bucket=bucket_name, Key=key, Body=bytes_data)


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

    args = parser.parse_args()
    if args.which == "ls":
        await handle_bucket_ls(bucket_name=args.bucket)
    elif args.which == "download":
        await handle_download_object(bucket_name=args.bucket, key=args.key, dst_folder=args.destination)
    elif args.which == "upload_folder":
        await handle_upload_folder(bucket_name=args.bucket, path=args.directory)


if __name__ == "__main__":
    asyncio.run(main())
