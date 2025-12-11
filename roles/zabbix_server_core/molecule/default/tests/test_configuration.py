"""
Zabbix Server configuration tests
"""


def test_config_file_exists(host, zabbix_vars):
    """Zabbix Serverの設定ファイルが存在することを確認する"""
    conf_file = zabbix_vars["zabbix_server_core_conf_file"]
    f = host.file(conf_file)

    assert f.exists
    assert f.is_file
    assert f.user == "zabbix"
    assert f.group == "zabbix"
    assert f.mode == 0o640


def test_conf_d_directory_exists(host, zabbix_vars):
    """拡張性確認: zabbix_server.conf.d ディレクトリが存在することを確認する"""
    conf_dir = zabbix_vars["zabbix_server_core_conf_dir"]
    d = host.file(conf_dir)

    assert d.exists
    assert d.is_directory
    assert d.user == "zabbix"
    assert d.group == "zabbix"
    assert d.mode == 0o750


def test_config_includes_conf_d(host, zabbix_vars):
    """設定ファイルにconf.dディレクトリのIncludeが含まれていることを確認する"""
    conf_file = zabbix_vars["zabbix_server_core_conf_file"]
    conf_dir = zabbix_vars["zabbix_server_core_conf_dir"]

    f = host.file(conf_file)
    assert f.contains(f"Include={conf_dir}/\\*.conf")
