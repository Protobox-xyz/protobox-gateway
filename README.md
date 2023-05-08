# Protobox Gateway — S3 Gateway to Swarm 🐝 ![GitHub](https://img.shields.io/github/license/protobox-xyz/protobox-gateway?style=plastic) 

Protobox is a decentralized storage product and suite of tools that allow existing web2 customers who utilize object storage solutions (including AWS S3) to easily access the inherent benefits of distributed storage networks.

The Protobox S3 API enables data transfer from S3 API-compatible storage endpoints/vendors to [Ethereum Swarm](https://github.com/ethersphere).

# Contents 🔍
+ [Getting Started](https://github.com/Protobox-xyz/protobox-gateway/edit/main/README.md#getting-started)
  + [Prerequisites](https://github.com/Protobox-xyz/protobox-gateway/edit/main/README.md#prerequisites)
  + [Configuration and Installation](https://github.com/Protobox-xyz/protobox-gateway/edit/main/README.md#configuration-and-installation)
+ [S3 Compatible API](https://github.com/Protobox-xyz/protobox-gateway/edit/main/README.md#s3-compatible-api-)
  + [API Endpoint](https://github.com/Protobox-xyz/protobox-gateway/edit/main/README.md#api-endpoint)
  + [Supported API Actions](https://github.com/Protobox-xyz/protobox-gateway/edit/main/README.md#supported-api-actions)
  + [Using AWS S3 SDK](https://github.com/Protobox-xyz/protobox-gateway/edit/main/README.md#using-aws-s3-sdk)
+ [Additional Resources](https://github.com/Protobox-xyz/protobox-gateway/edit/main/README.md#additional-resources-)
+ [Team](https://github.com/Protobox-xyz/protobox-gateway/edit/main/README.md#team-)
+ [Contributions/Feedback](https://github.com/Protobox-xyz/protobox-gateway/edit/main/README.md#contributions-and-feedback-%EF%B8%8F)
+ [Show Your Support](https://github.com/Protobox-xyz/protobox-gateway/edit/main/README.md#show-your-support)
+ [License](https://github.com/Protobox-xyz/protobox-gateway/edit/main/README.md#license-)

📄 _An alternate form of our documentation can be found via our [Gitbook](https://docs.protobox.xyz/protobox-overview/what-is-protobox)_

## Getting Started

### Prerequisites
+ Docker (latest) with compose
+ MongoDB (latest)
+ Git

### Configuration and Installation
+ Clone the project on the desired swarm endpoint
+ Create a MongoDB instance for usage by the gateway
+ Edit the docker-compose.yml with details of your SSL certificats, mongoDB credentials, and swarm node location
+ Run:
~~~~
docker compose up
~~~~

## S3 Compatible API 🔌

### API Endpoint

The Protobox S3-compatible API endpoint URL is: 
~~~~
https://s3.protobox.xyz
~~~~~

### Supported API Actions

Protobox currently supports the following S3 API actions:

| Action      | Function |
| ----------- | ----------- |
| CreateBucket      | Creates a new S3 bucket. See here for bucket naming conventions.      |
| DeleteBucket   | Deletes the S3 bucket. All objects in a bucket must be deleted before the bucket itself can be deleted.        |
| DeleteObject | Removes the specified object.  |
| GetObject | Retrieves objects from S3. |
| HeadObject | This command will return the metadata of the file if it exists. If the file does not exist, the command will return an error message. |
| ListBuckets | Lists all of the buckets you own. |
| ListObjects | Returns some or all (up to 1,000) of the objects in a bucket. |
| PutObject | Adds an object to a specifed bucket. |


### Using AWS S3 SDK

Below is an example of using [AWS S3 SDK for Python](https://github.com/Protobox-xyz/swarm-sdk) to manage files in Swarm.

~~~~
import boto3
import botocore.config

session = boto3.session.Session()

return session.client(
    "s3",
    endpoint_url="https://s3.protobox.xyz/",
    aws_session_token=BATCH_ID,
    aws_secret_access_key=BATCH_ID,
    aws_access_key_id=BATCH_ID,
)
~~~~

## Additional Resources 📙
Please refer to our Gitbook for [additional resources](https://docs.protobox.xyz/resources/glossary)

## Team 👥
[Maintainers](https://github.com/orgs/Protobox-xyz/people)


### Contributions and Feedback 🖋️
For partnerships and integrations, please reach out to us at team@protobox.xyz.

### Show your support
+ Please ⭐️ this repository if you find it useful!
+ [Follow our Twitter](https://twitter.com/protobox_xyz) for updates and announcements.

## License 📜

[MIT License](https://github.com/Protobox-xyz/protobox-gateway/blob/main/LICENSE) | Copyright (c) 2023 Protobox
