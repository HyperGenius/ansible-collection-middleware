"""
Zabbix Config tests
Zabbix APIを使用して設定が正しく反映されているか確認する
"""
import pytest
import requests


def test_zabbix_api_authentication(host):
    """
    Zabbix APIで認証できることを確認する
    """
    api_url = "http://localhost/zabbix/api_jsonrpc.php"
    headers = {"Content-Type": "application/json-rpc"}
    
    # API認証リクエスト
    auth_payload = {
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {
            "username": "Admin",
            "password": "zabbix"
        },
        "id": 1
    }
    
    response = requests.post(api_url, json=auth_payload, headers=headers)
    assert response.status_code == 200
    
    result = response.json()
    assert "result" in result
    assert result["result"] is not None  # トークンが取得できること


def test_auto_registration_action_exists(host):
    """
    自動登録アクションが作成されていることを確認する
    """
    api_url = "http://localhost/zabbix/api_jsonrpc.php"
    headers = {"Content-Type": "application/json-rpc"}
    
    # まず認証
    auth_payload = {
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {
            "username": "Admin",
            "password": "zabbix"
        },
        "id": 1
    }
    
    auth_response = requests.post(api_url, json=auth_payload, headers=headers)
    auth_token = auth_response.json()["result"]
    
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
        "auth": auth_token,
        "id": 2
    }
    
    action_response = requests.post(api_url, json=action_payload, headers=headers)
    assert action_response.status_code == 200
    
    actions = action_response.json()["result"]
    assert len(actions) > 0  # アクションが存在すること
    assert actions[0]["name"] == "Auto registration for Linux"


def test_auto_registration_action_conditions(host):
    """
    自動登録アクションの条件が正しく設定されていることを確認する
    """
    api_url = "http://localhost/zabbix/api_jsonrpc.php"
    headers = {"Content-Type": "application/json-rpc"}
    
    # まず認証
    auth_payload = {
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {
            "username": "Admin",
            "password": "zabbix"
        },
        "id": 1
    }
    
    auth_response = requests.post(api_url, json=auth_payload, headers=headers)
    auth_token = auth_response.json()["result"]
    
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
        "auth": auth_token,
        "id": 2
    }
    
    action_response = requests.post(api_url, json=action_payload, headers=headers)
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


def test_host_group_exists(host):
    """
    自動登録先のホストグループが作成されていることを確認する
    """
    api_url = "http://localhost/zabbix/api_jsonrpc.php"
    headers = {"Content-Type": "application/json-rpc"}
    
    # まず認証
    auth_payload = {
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {
            "username": "Admin",
            "password": "zabbix"
        },
        "id": 1
    }
    
    auth_response = requests.post(api_url, json=auth_payload, headers=headers)
    auth_token = auth_response.json()["result"]
    
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
        "auth": auth_token,
        "id": 3
    }
    
    group_response = requests.post(api_url, json=group_payload, headers=headers)
    assert group_response.status_code == 200
    
    groups = group_response.json()["result"]
    assert len(groups) > 0  # ホストグループが存在すること
    assert groups[0]["name"] == "Linux servers"
