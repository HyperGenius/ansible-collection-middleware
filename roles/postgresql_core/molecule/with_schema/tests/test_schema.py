def test_sample_table_exists(host):
    """
    sample_db内のusersテーブルが存在し、SELECTクエリが成功することを確認する。
    """
    # psqlコマンドでテーブルに対してSELECTクエリを実行
    # -d sample_db : データベース指定
    # -c ...       : SQL実行
    cmd = host.run("sudo -u postgres psql -d sample_db -c \"SELECT count(*) FROM users;\"")
    
    # 実行が成功し (戻り値 0)、結果に 'count' の文字が含まれていることを確認
    assert cmd.rc == 0
    assert "count" in cmd.stdout
