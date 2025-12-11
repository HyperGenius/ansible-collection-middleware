"""
Pytest configuration for zabbix_config tests
"""
import json
import pytest


@pytest.fixture(scope="module")
def zabbix_config_vars(host):
    """
    Zabbix設定変数をロードする
    """
    vars_file = "/tmp/zabbix_config_vars.json"
    with host.file(vars_file).content as f:
        return json.loads(f)
