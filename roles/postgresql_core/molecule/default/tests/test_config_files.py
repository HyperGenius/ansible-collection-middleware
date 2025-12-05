def test_config_files(host):
    """PostgreSQLの設定ファイルと所有者、権限が正しく設定されていることを確認する"""
    base_dir = "/var/lib/pgsql/14/data"  # TODO: バージョンを動的に取得する
    conf_file = host.file(f"{base_dir}/postgresql.conf")
    hba_file = host.file(f"{base_dir}/pg_hba.conf")

    # postgresql.confの確認
    assert conf_file.exists
    assert conf_file.user == "postgres"
    assert conf_file.group == "postgres"
    assert conf_file.mode == 0o600

    # pg_hba.confの確認
    assert hba_file.exists
    assert hba_file.user == "postgres"
    assert hba_file.group == "postgres"
    assert hba_file.mode == 0o600
