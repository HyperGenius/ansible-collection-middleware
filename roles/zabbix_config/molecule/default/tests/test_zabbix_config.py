"""
Zabbix Config tests
Zabbix APIを使用して設定が正しく反映されているか確認する
"""
import pytest
import requests


# テスト用定数
ZABBIX_API_URL = "http://localhost/zabbix/api_jsonrpc.php"
ZABBIX_API_HEADERS = {"Content-Type": "application/json-rpc"}
ZABBIX_ADMIN_USER = "Admin"
ZABBIX_ADMIN_PASSWORD = "zabbix"


@pytest.fixture(scope="module")
def zabbix_auth_token():
    """
    Zabbix API認証トークンを取得するフィクスチャ
    """
    auth_payload = {
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {
            "username": ZABBIX_ADMIN_USER,
            "password": ZABBIX_ADMIN_PASSWORD
        },
        "id": 1
    }
    
    response = requests.post(ZABBIX_API_URL, json=auth_payload, headers=ZABBIX_API_HEADERS)
    assert response.status_code == 200
    
    result = response.json()
    assert "result" in result
    assert result["result"] is not None
    
    return result["result"]


def test_zabbix_api_authentication(zabbix_auth_token):
    """
    Zabbix APIで認証できることを確認する
    """
    # フィクスチャでトークンが取得できていれば成功
    assert zabbix_auth_token is not None


def test_auto_registration_action_exists(zabbix_auth_token):
    """
    自動登録アクションが作成されていることを確認する
    """
    # アクション取得
    action_payload = {
        "jsonrpc": "2.0",
        "method": "action.get",
        "params": {
            "output": "extend",
            "filter": {
                "name": "Auto registration for Linux"
            }
        },
        "auth": zabbix_auth_token,
        "id": 2
    }
    
    action_response = requests.post(ZABBIX_API_URL, json=action_payload, headers=ZABBIX_API_HEADERS)
    assert action_response.status_code == 200
    
    actions = action_response.json()["result"]
    assert len(actions) > 0  # アクションが存在すること
    assert actions[0]["name"] == "Auto registration for Linux"


def test_auto_registration_action_conditions(zabbix_auth_token):
    """
    自動登録アクションの条件が正しく設定されていることを確認する
    """
    # アクション取得（条件含む）
    action_payload = {
        "jsonrpc": "2.0",
        "method": "action.get",
        "params": {
            "output": "extend",
            "selectFilter": "extend",
            "filter": {
                "name": "Auto registration for Linux"
            }
        },
        "auth": zabbix_auth_token,
        "id": 2
    }
    
    action_response = requests.post(ZABBIX_API_URL, json=action_payload, headers=ZABBIX_API_HEADERS)
    assert action_response.status_code == 200
    
    actions = action_response.json()["result"]
    assert len(actions) > 0
    
    action = actions[0]
    # 条件にHostMetadata likeが含まれていることを確認
    conditions = action.get("filter", {}).get("conditions", [])
    
    # 条件が設定されていること
    assert len(conditions) > 0
    
    # HostMetadata条件が含まれていること
    metadata_condition_found = False
    for condition in conditions:
        if condition.get("conditiontype") == "24":  # 24 = Host metadata
            metadata_condition_found = True
            assert "Linux" in condition.get("value", "")
    
    assert metadata_condition_found, "HostMetadata条件が見つかりません"


def test_host_group_exists(zabbix_auth_token):
    """
    自動登録先のホストグループが作成されていることを確認する
    """
    # ホストグループ取得
    group_payload = {
        "jsonrpc": "2.0",
        "method": "hostgroup.get",
        "params": {
            "output": "extend",
            "filter": {
                "name": "Linux servers"
            }
        },
        "auth": zabbix_auth_token,
        "id": 3
    }
    
    group_response = requests.post(ZABBIX_API_URL, json=group_payload, headers=ZABBIX_API_HEADERS)
    assert group_response.status_code == 200
    
    groups = group_response.json()["result"]
    assert len(groups) > 0  # ホストグループが存在すること
    assert groups[0]["name"] == "Linux servers"
