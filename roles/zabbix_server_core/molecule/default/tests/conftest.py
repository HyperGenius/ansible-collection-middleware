"""
Pytest fixtures for Zabbix Server tests
"""
import pytest


@pytest.fixture()
def zabbix_vars(host):
    """Zabbix Server変数を取得する"""
    defaults = host.ansible("include_vars", "file=defaults/main.yml")["ansible_facts"]
    vars_file = host.ansible("include_vars", "file=vars/main.yml")["ansible_facts"]
    
    return {
        "service_name": vars_file["zabbix_server_core_service_name"],
        "package_name": vars_file["zabbix_server_core_package_name"],
        "conf_file": vars_file["zabbix_server_core_conf_file"],
        "conf_dir": vars_file["zabbix_server_core_conf_dir"],
        "log_file": vars_file["zabbix_server_core_log_file"],
        "listen_port": defaults["zabbix_server_core_listen_port"],
    }
