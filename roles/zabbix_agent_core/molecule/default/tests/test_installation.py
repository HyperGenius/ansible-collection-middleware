"""
Zabbix Agent 2 installation tests
"""


def test_zabbix_agent_package_installed(host):
    """Zabbix Agent 2 package is installed"""
    pkg = host.package("zabbix-agent2")
    assert pkg.is_installed


def test_zabbix_agent_config_file_exists(host, zabbix_vars):
    """Zabbix Agent 2 configuration file exists"""
    config_file = zabbix_vars["zabbix_agent_core_config_file_linux"]
    f = host.file(config_file)
    
    assert f.exists
    assert f.is_file
    assert f.user == "root"
    assert f.group == "root"


def test_zabbix_agent_include_dir_exists(host, zabbix_vars):
    """Zabbix Agent 2 include directory exists"""
    include_dir = zabbix_vars["zabbix_agent_core_include_dir"]
    d = host.file(include_dir)
    
    assert d.exists
    assert d.is_directory
    assert d.user == "zabbix"
    assert d.group == "zabbix"
