def test_postgresql_service(host, postgresql_vars):
    """PostgreSQLサービスが正しく設定されていることを確認する"""
    service_name = postgresql_vars["service_name"]

    service = host.service(service_name)

    # PostgreSQLサービスが起動していること (is_running)
    assert service.is_running

    # PostgreSQLサービスが自動起動設定になっていること (is_enabled)
    assert service.is_enabled
