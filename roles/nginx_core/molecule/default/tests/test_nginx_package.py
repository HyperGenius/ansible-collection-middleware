def test_nginx_package_installed(host, nginx_vars):
    """Nginxパッケージがインストールされているか確認"""
    pkg_name = nginx_vars["nginx_package_name"]
    pkg = host.package(pkg_name)
    assert pkg.is_installed
