def test_existing_users_table_on_postgresql(host, zabbix_vars):
    """usersテーブルが存在することを確認する"""
    pgpassword = zabbix_vars["zabbix_server_core_db_password"]

    # usersテーブルが存在することを確認
    cmd = host.run(
        f"PGPASSWORD={pgpassword} psql -h localhost -U zabbix -d zabbix -tAc "
        '"SELECT COUNT(*) FROM information_schema.tables '
        "WHERE table_schema = 'public' AND table_name = 'users'\""
    )

    assert cmd.rc == 0
    assert cmd.stdout.strip() == "1"


def test_default_admin_user_exists(host, zabbix_vars):
    """デフォルトのAdminユーザーが存在することを確認する"""
    pgpassword = zabbix_vars["zabbix_server_core_db_password"]

    # usersテーブルにデフォルトのAdminユーザーが存在することを確認
    cmd = host.run(
        f"PGPASSWORD={pgpassword} psql -h localhost -U zabbix -d zabbix -tAc "
        "\"SELECT COUNT(*) FROM users WHERE username = 'Admin'\""
    )

    assert cmd.rc == 0
    assert int(cmd.stdout.strip()) >= 1
