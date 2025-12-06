def test_nginx_service_running_and_enabled(host, nginx_vars):
    """Nginxサービスが起動中かつ自動起動設定されているか確認"""
    service_name = nginx_vars["nginx_service_name"]
    service = host.service(service_name)
    assert service.is_running
    assert service.is_enabled
