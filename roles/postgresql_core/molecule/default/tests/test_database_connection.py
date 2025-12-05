def test_database_connection(host, postgresql_vars):
    """PostgreSQLのポート設定が正しいことを確認する"""
    # 【仕様】: ポート5432でリッスンしていること
    # 【仕様】: 実際にローカルから接続してSQLが実行できること (例: SELECT 1)
    # ポート確認
    # RHEL/CentOS系ではデフォルトでlocalhostではなく全インターフェース(あるいは設定による)でlistenすることが多い
    # ここではlisten_addresses = '*' を前提とするなら 0.0.0.0:5432 もしくは :::5432
    port = postgresql_vars["port"]
    socket = host.socket(f"tcp://0.0.0.0:{port}")
    assert socket.is_listening

    # 接続確認: postgresユーザーでpsqlコマンドを実行
    cmd = host.run("sudo -u postgres psql -c 'SELECT 1'")
    assert cmd.rc == 0
