"""
Zabbix Server installation tests
"""


def test_zabbix_package_installed(host, zabbix_vars):
    """Zabbix Serverパッケージがインストールされていることを確認する"""
    package_name = zabbix_vars["zabbix_server_core_package_name"]
    p = host.package(package_name)
    assert p.is_installed


def test_sql_scripts_package_installed(host):
    """Zabbix SQL scriptsパッケージがインストールされていることを確認する"""
    p = host.package("zabbix-sql-scripts")
    assert p.is_installed
