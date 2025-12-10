def test_nginx_service_running(host):
    """Nginxサービスが起動していることを確認する"""
    service = host.service("nginx")

    # Nginxサービスが起動していること (is_running)
    assert service.is_running

    # Nginxサービスが自動起動設定になっていること (is_enabled)
    assert service.is_enabled


def test_nginx_port_80_listening(host):
    """Nginxがポート80でリッスンしていることを確認する"""
    socket = host.socket("tcp://0.0.0.0:80")
    assert socket.is_listening
