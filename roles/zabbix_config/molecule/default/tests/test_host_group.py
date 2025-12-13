from tests.helpers import post_zabbix_api


def test_host_group_exists(zabbix_config_vars):
    """
    自動登録先のホストグループが作成されていることを確認する
    """

    # パラメータ取得
    expected_group_name = zabbix_config_vars["zabbix_config_autoreg_group"]

    # ホストグループ取得
    group_payload = {
        "jsonrpc": "2.0",
        "method": "hostgroup.get",
        "params": {"output": "extend", "sortfield": "name"},
        "id": 3,
    }

    group_response = post_zabbix_api(zabbix_config_vars, group_payload)
    assert group_response.status_code == 200
    assert "result" in group_response.json()

    groups = group_response.json()["result"]

    assert [group for group in groups if group["name"] == expected_group_name]
