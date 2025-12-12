import requests

# Zabbix API定数
CONDITION_TYPE_HOST_METADATA = "24"  # ホストメタデータ条件タイプ


def test_auto_registration_action_exists(zabbix_config_vars):
    """
    自動登録アクションが作成されていることを確認する
    """

    # パラメータ取得
    api_url = zabbix_config_vars["zabbix_api_url"]
    auth_token = zabbix_config_vars["zabbix_auth_token"]
    auto_registration_action_name = zabbix_config_vars["zabbix_config_autoreg_name"]

    # アクション取得
    action_payload = {
        "jsonrpc": "2.0",
        "method": "action.get",
        "params": {
            "output": "extend",
            "filter": {"name": auto_registration_action_name},
        },
        "id": 2,
    }

    action_response = requests.post(
        api_url,
        json=action_payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + auth_token,
        },
        timeout=30,
    )
    assert action_response.status_code == 200

    actions = action_response.json()["result"]
    assert len(actions) > 0  # アクションが存在すること
    assert actions[0]["name"] == auto_registration_action_name


def test_auto_registration_action_conditions(zabbix_config_vars):
    """
    自動登録アクションの条件が正しく設定されていることを確認する
    """

    # パラメータ取得
    api_url = zabbix_config_vars["zabbix_api_url"]
    auth_token = zabbix_config_vars["zabbix_auth_token"]
    expected_group_name = zabbix_config_vars["zabbix_config_autoreg_group"]
    auto_registration_action_name = zabbix_config_vars["zabbix_config_autoreg_name"]

    # アクション取得（条件含む）
    action_payload = {
        "jsonrpc": "2.0",
        "method": "action.get",
        "params": {
            "output": "extend",
            "selectFilter": "extend",
            "filter": {"name": auto_registration_action_name},
        },
        "id": 2,
    }

    action_response = requests.post(
        api_url,
        json=action_payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + auth_token,
        },
        timeout=30,
    )
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
        if condition.get("conditiontype") == CONDITION_TYPE_HOST_METADATA:
            metadata_condition_found = True
            assert "Linux" in condition.get("value", "")

    assert metadata_condition_found, "HostMetadata条件が見つかりません"
