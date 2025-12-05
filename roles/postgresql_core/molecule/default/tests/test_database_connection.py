def test_database_connection(host):
    """PostgreSQLのポート設定が正しいことを確認する"""
    # ポート確認
    # RHEL/CentOS系ではデフォルトでlocalhostではなく全インターフェース(あるいは設定による)でlistenすることが多い
    # ここではlisten_addresses = '*' を前提とするなら 0.0.0.0:5432 もしくは :::5432
    socket = host.socket("tcp://0.0.0.0:5432")  # TODO: バージョンを動的に取得する
    assert socket.is_listening

    # 接続確認: postgresユーザーでpsqlコマンドを実行
    cmd = host.run("sudo -u postgres psql -c 'SELECT 1'")
    assert cmd.rc == 0
