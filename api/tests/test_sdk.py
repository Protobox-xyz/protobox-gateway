import pytest

from swarm_sdk.sdk import SwarmClient


@pytest.mark.skip()
def test_swarm_sdk():
    swarm = SwarmClient(
        batch_id="b2432619b1e74aed26d7174a0601fe60aac617307114295ff9f715b8b88a6aaa",
        server_url="http://104.237.159.189:1633/bzz",
    )

    result = swarm.upload("/home/soso/Pictures/screenshot.png")
    print(result)
