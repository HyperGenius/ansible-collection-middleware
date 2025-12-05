def test_postgresql_service(host):
    """PostgreSQLサービスが正しく設定されていることを確認する"""
    service = host.service("postgresql-14")  # TODO: バージョンを動的に取得する

    # PostgreSQLサービスが起動していること (is_running)
    assert service.is_running

    # PostgreSQLサービスが自動起動設定になっていること (is_enabled)
    assert service.is_enabled
