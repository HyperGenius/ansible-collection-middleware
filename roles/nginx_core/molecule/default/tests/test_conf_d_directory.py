def test_conf_d_directory_permission(host, nginx_vars):
    """拡張設定ディレクトリの権限確認"""
    conf_d = nginx_vars["nginx_conf_d_dir"]
    d = host.file(conf_d)
    assert d.is_directory
    assert d.user == "root"
    assert d.group == "root"
    assert d.mode == 0o755
