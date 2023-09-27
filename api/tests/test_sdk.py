import pytest
from swarm_sdk.exceptions import BatchIDRequiredException
from swarm_sdk.sdk import SwarmClient


@pytest.mark.asyncio
async def test_swarm_sdk_upload_from_bytes(mocker):
    requests_mock = mocker.patch("aiohttp.ClientSession.post")
    swarm = SwarmClient(
        batch_id="b2432619b1e74aed26d7174a0601fe60aac617307114295ff9f715b8b88a6aaa",
        server_url="http://104.237.159.189:1633/bzz",
    )

    data = b"Lorem ipsum text generator is a free online tool for generating dummy text or lipsum.\n"
    await swarm.upload(data, content_type="text/plain", name="text_file.txt")
    headers = {
        "Content-Type": "text/plain",
        "Swarm-Postage-Batch-Id": "b2432619b1e74aed26d7174a0601fe60aac617307114295ff9f715b8b88a6aaa",
    }
    requests_mock.assert_called_once()
    args, kwargs = requests_mock.call_args_list[0]
    assert kwargs["params"] == {"name": "text_file.txt"}
    assert kwargs["headers"] == headers
    assert kwargs["data"] == data


@pytest.mark.asyncio
async def test_swarm_sdk_upload_from_file_without_batch_id():
    swarm = SwarmClient(
        batch_id=None,
        server_url="http://some-server.com/bzz",
    )
    with pytest.raises(BatchIDRequiredException):
        await swarm.upload("./tests/data/text_file.txt", name="text_file.txt")


@pytest.mark.asyncio
async def test_swarm_sdk_download_file(mocker):
    requests_mock = mocker.patch("aiohttp.ClientSession.get")
    swarm = SwarmClient(
        batch_id=None,
        server_url="http://some-server.com/bzz",
    )

    await swarm.download("some-file-id")
    requests_mock.assert_called_once()
    args, kwargs = requests_mock.call_args_list[0]
    assert args[0] == "http://some-server.com/bzz/some-file-id/"
