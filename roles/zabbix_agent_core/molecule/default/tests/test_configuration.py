"""
Zabbix Agent 2 configuration tests
"""


def test_zabbix_agent_config_server(host, zabbix_vars):
    """Zabbix Agent configuration contains correct Server setting"""
    config_file = zabbix_vars["zabbix_agent_core_config_file"]
    expected_server = zabbix_vars["zabbix_agent_core_server"]

    f = host.file(config_file)
    assert f.contains(f"Server={expected_server}")


def test_zabbix_agent_config_server_active(host, zabbix_vars):
    """Zabbix Agent configuration contains correct ServerActive setting"""
    config_file = zabbix_vars["zabbix_agent_core_config_file"]
    expected_server_active = zabbix_vars["zabbix_agent_core_server_active"]

    f = host.file(config_file)
    assert f.contains(f"ServerActive={expected_server_active}")


def test_zabbix_agent_config_hostname(host, zabbix_vars):
    """Zabbix Agent configuration contains correct Hostname setting"""
    config_file = zabbix_vars["zabbix_agent_core_config_file"]
    expected_hostname = zabbix_vars["zabbix_agent_core_hostname"]

    f = host.file(config_file)
    assert f.contains(f"Hostname={expected_hostname}")


def test_zabbix_agent_config_host_metadata(host, zabbix_vars):
    """Zabbix Agent configuration contains HostMetadata setting"""
    config_file = zabbix_vars["zabbix_agent_core_config_file"]
    expected_metadata = zabbix_vars["zabbix_agent_core_host_metadata"]

    f = host.file(config_file)
    assert f.contains(f"HostMetadata={expected_metadata}")


def test_zabbix_agent_config_include_dir(host, zabbix_vars):
    """Zabbix Agent configuration contains Include directive"""
    config_file = zabbix_vars["zabbix_agent_core_config_file"]
    include_dir = zabbix_vars["zabbix_agent_core_include_dir"]

    f = host.file(config_file)
    assert f.contains(f"Include={include_dir}/*.conf")
