"""
Pytest conftest for Zabbix Agent 2 tests
"""

import json
import os
import pytest
import requests
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture()
def zabbix_vars(host):
    """Load Zabbix Agent variables from JSON file"""
    vars_file = host.file("/tmp/test_data/zabbix_agent_vars.json")
    if not vars_file.exists:
        pytest.skip("Variable dump file not found")

    content = vars_file.content_string
    return json.loads(content)


def get_zabbix_api_url(
    zabbix_config_server_hostname: str, zabbix_config_server_port: int
) -> str:
    """
    Zabbix API URLを生成する
    """

    try:
        api_url = (
            "http://"
            + zabbix_config_server_hostname
            + f":{zabbix_config_server_port}"
            + "/api_jsonrpc.php"
        )
    except KeyError as e:
        raise ValueError(f"Required key not found in var_json: {e}")

    return api_url


def get_zabbix_auth_token(
    zabbix_server_hostname: str,
    zabbix_server_port: int,
) -> str:
    """
    Zabbix API認証トークンを取得するフィクスチャ
    """
    try:
        zabbix_api_user: str = os.environ["ZABBIX_API_USER"]
        zabbix_api_password: str = os.environ["ZABBIX_API_PASSWORD"]
    except KeyError as e:
        raise ValueError(f"Required key not found in var_json: {e}")

    url = get_zabbix_api_url(zabbix_server_hostname, zabbix_server_port)
    auth_payload = {
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {
            "username": zabbix_api_user,
            "password": zabbix_api_password,
        },
        "id": 1,
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(
        url,
        json=auth_payload,
        headers=headers,
        timeout=30,
    )
    assert response.status_code == 200

    result = response.json()
    assert "result" in result
    assert result["result"] is not None

    return result["result"]
