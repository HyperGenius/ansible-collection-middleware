def test_database_connection(host, postgresql_vars):
    """PostgreSQLのポート設定が正しいことを確認する"""

    # ポート確認
    port = postgresql_vars["port"]
    socket = host.socket(f"tcp://0.0.0.0:{port}")
    assert socket.is_listening

    # 接続確認: postgresユーザーでpsqlコマンドを実行
    cmd = host.run("sudo -u postgres psql -c 'SELECT 1'")
    assert cmd.rc == 0
