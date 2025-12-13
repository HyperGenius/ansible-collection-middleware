import os
import json
import pytest
import requests
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"]
).get_hosts("all")

DUMPED_VARS_FILE = "/tmp/ansible_vars.json"


@pytest.fixture()
def zabbix_config_vars(host):
    """コンテナ内にダンプされたAnsible変数を読み込むフィクスチャ"""
    vars_file = host.file(DUMPED_VARS_FILE)

    if not vars_file.exists:
        pytest.skip("ダンプされた変数ファイルが見つかりません")

    try:
        vars_json = json.loads(vars_file.content_string)
    except json.JSONDecodeError:
        pytest.fail("ダンプされた変数ファイルの内容がJSON形式ではありません")

    vars_json["zabbix_api_url"] = get_zabbix_api_url(vars_json)
    vars_json["zabbix_auth_token"] = get_zabbix_auth_token(vars_json)

    return vars_json


def get_zabbix_api_url(var_json: dict) -> str:
    """
    Zabbix API URLを生成する
    """

    try:
        api_url = (
            "http://"
            + var_json["zabbix_config_server_hostname"]
            + f':{var_json["zabbix_config_server_port"]}'
            + "/api_jsonrpc.php"
        )
    except KeyError as e:
        raise ValueError(f"Required key not found in var_json: {e}")

    return api_url


def get_zabbix_auth_token(var_json: dict) -> str:
    """
    Zabbix API認証トークンを取得するフィクスチャ
    """
    url = get_zabbix_api_url(var_json)
    auth_payload = {
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {
            "username": var_json["zabbix_config_api_user"],
            "password": var_json["zabbix_config_api_password"],
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
