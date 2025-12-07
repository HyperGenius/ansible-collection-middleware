def test_tomcat_port(host):
    # 【仕様】: ポート 8080 でリッスンしていること (TCP)
    # Tomcatは起動に時間がかかるため、必要ならリトライ待ちを入れるか、
    # Ansible側で `wait_for` 済みの状態でテストする
    pass
