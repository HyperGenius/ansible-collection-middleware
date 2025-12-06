def test_nginx_port_listening(host, nginx_vars):
    """Nginxが指定ポートでリッスンしているか確認"""
    port = nginx_vars["nginx_http_port"]
    # IPv4/IPv6のどちらかでリッスンしていればOKとする
    # 環境によって tcp://:::80 と表現される場合もあるため緩めにチェック
    socket_v4 = host.socket(f"tcp://0.0.0.0:{port}")
    socket_v6 = host.socket(f"tcp://:::{port}")

    # ポートだけ指定してチェックすることも可能だが、testinfraの仕様に合わせて実装
    assert (
        socket_v4.is_listening
        or socket_v6.is_listening
        or host.socket(f"tcp://{port}").is_listening
    )
