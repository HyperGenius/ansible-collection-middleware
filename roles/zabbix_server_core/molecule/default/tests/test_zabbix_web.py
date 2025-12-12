def test_zabbix_web_index(host):
    """
    Zabbix Web UI (index.php) が正常に表示されるか確認
    """
    # -L: リダイレクトを追跡 (ログイン画面に飛ばされるため)
    # -k: SSL検証無視 (今回はhttpなので関係ないが汎用的に)
    # -I: ヘッダのみ取得
    cmd = host.run("curl -L -k -I http://localhost/index.php")

    # 接続成功 (200 OK) であること
    # 設定によっては 301/302 Redirect になる場合もあるので、200番台か300番台ならOKとする
    assert cmd.rc == 0
    assert "HTTP/1.1 200" in cmd.stdout or "HTTP/1.1 30" in cmd.stdout


def test_zabbix_api_endpoint(host):
    """
    Zabbix API (api_jsonrpc.php) が JSON を返すか確認
    """
    # ヘッダ情報に 'Content-Type: application/json' が含まれているべき
    # POSTメソッドで空打ちすると通常はエラーJSONが返るが、ステータスは 200 OK になるはず
    cmd = host.run(
        "curl -X POST -H 'Content-Type: application/json' -d '{}' -i http://localhost/api_jsonrpc.php"
    )

    assert cmd.rc == 0
    assert "HTTP/1.1 200 OK" in cmd.stdout
    # PHP-FPMが正しく動いていれば JSON で返ってくる
    assert "application/json" in cmd.stdout
