import pytest

from utils.auth import extract_token_from_aws_v4_auth_header


@pytest.mark.parametrize(
    "auth_header, expected_token",
    [
        (
            "AWS4-HMAC-SHA256 Credential=3d7d23da1b8a34adc286b04f60e49138cf724ffd234831c4899103cec623b796/20230423/ignored/s3/aws4_request, SignedHeaders=content-length;content-md5;content-type;host;x-amz-content-sha256;x-amz-date, Signature=d398e8fa53551a2dc067af9b8794078de604c7cac943c84f025b421284e9e7d9",
            "3d7d23da1b8a34adc286b04f60e49138cf724ffd234831c4899103cec623b796",
        ),
    ],
)
def test_extract_token_from_aws_v4_auth_header(auth_header: str, expected_token: str):
    token = extract_token_from_aws_v4_auth_header(auth_header)
    assert token == expected_token
