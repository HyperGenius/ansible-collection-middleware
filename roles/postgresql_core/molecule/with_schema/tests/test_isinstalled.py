def test_postgresql_is_installed(host, postgresql_vars):
    """PostgreSQLのパッケージがインストールされていることを確認する"""
    package_name = postgresql_vars["package_name"]
    p = host.package(package_name)
    assert p.is_installed
