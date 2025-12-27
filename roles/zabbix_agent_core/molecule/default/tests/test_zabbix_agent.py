"""
Zabbix Agent 2 サービスのテスト
"""


def test_zabbix_agent_service_running(host, zabbix_vars):
    """Zabbix Agent 2 サービスが実行されている"""
    service_name = zabbix_vars["zabbix_agent_core_service_name"]
    service = host.service(service_name)

    # Zabbix Agent 2 service is running (is_running)
    assert service.is_running

    # Zabbix Agent 2 service is enabled (is_enabled)
    assert service.is_enabled


def test_zabbix_agent_port_listening(host, zabbix_vars):
    """Zabbix Agent 2 が指定されたポートでリッスンしている"""
    listen_port = zabbix_vars["zabbix_agent_core_listen_port"]

    # Check that the agent is listening on the specified port
    socket = host.socket(f"tcp://0.0.0.0:{listen_port}")
    assert socket.is_listening
