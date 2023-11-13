from pathlib import Path
import asyncio
import argparse

import boto3
import os

ENDPOINT_URL = "http://localhost:8000/"
BATCH_ID = "b00b92417dd7d5c379dba70afd4f986675e05df2635beab6ff2a6eb6eb8b2208"
TOKEN = "18c431133dab8db77ef236d5a95b2a5a5b850132eeca1dafa34edbc709195231/0x18a22dc629c07c02cbba3942ce3b977db76d23bc08e722eb6be42a5b6d6d7a8d02e271a6e88895a8662d5339d33efc8ca442299a01e5b5becc3145b5f01eea5c1c"


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


async def bucket_ls(bucket_name: str):
    client = await get_client()
    print(client.list_objects(Bucket=bucket_name))


async def download_object(bucket_name: str, key: str, dst_folder: str):
    client = await get_client()
    data = client.get_object(Bucket=bucket_name, Key=key)
    file_path = os.path.join(dst_folder, key)

    # Get the directory of the file
    directory = os.path.dirname(file_path)
    Path(directory).mkdir(parents=True, exist_ok=True)
    with open(file_path, "wb") as file:
        file.write(data["Body"].read())


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

    args = parser.parse_args()
    if args.which == "ls":
        await bucket_ls(bucket_name=args.bucket)
    elif args.which == "download":
        await download_object(bucket_name=args.bucket, key=args.key, dst_folder=args.destination)


if __name__ == "__main__":
    asyncio.run(main())
