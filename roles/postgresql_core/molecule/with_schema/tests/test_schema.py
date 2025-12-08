def test_sample_table_exists(host):
    """sample_db内のusersテーブルが存在し、SELECTクエリが成功することを確認する"""
    cmd = host.run(
        'sudo -u postgres psql -d sample_db -c "SELECT count(*) FROM users;"'
    )
    assert cmd.rc == 0
    assert "count" in cmd.stdout
