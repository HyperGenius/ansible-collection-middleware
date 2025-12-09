"""
Zabbix Server service tests
"""


def test_zabbix_service_running(host, zabbix_vars):
    """Zabbix Serverサービスが起動していることを確認する"""
    service_name = zabbix_vars["service_name"]
    service = host.service(service_name)
    
    # Zabbix Serverサービスが起動していること (is_running)
    assert service.is_running
    
    # Zabbix Serverサービスが自動起動設定になっていること (is_enabled)
    assert service.is_enabled


def test_zabbix_port_listening(host, zabbix_vars):
    """Zabbix ServerがTCP 10051でリッスンしていることを確認する"""
    listen_port = zabbix_vars["listen_port"]
    
    # ポート10051でリッスンしていることを確認
    socket = host.socket(f"tcp://0.0.0.0:{listen_port}")
    assert socket.is_listening


def test_zabbix_log_no_database_errors(host, zabbix_vars):
    """Zabbix Serverのログファイルにデータベースエラーがないことを確認する"""
    log_file = zabbix_vars["log_file"]
    
    # ログファイルが存在することを確認
    log = host.file(log_file)
    assert log.exists
    
    # "database is down" エラーが含まれていないことを確認
    # Note: ログファイルが大きい場合は最後の100行程度をチェック
    cmd = host.run(f"tail -100 {log_file}")
    assert "database is down" not in cmd.stdout.lower()
