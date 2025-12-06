def test_nginx_config_syntax(host):
    """Nginx設定ファイルの構文チェック"""
    cmd = host.run("nginx -t")
    assert cmd.succeeded
