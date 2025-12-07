def test_java_installation(host, tomcat_vars):
    """Java (OpenJDK) パッケージがインストールされていること"""
    cmd_pkg = host.run("rpm -qa | grep java-.*-openjdk")
    assert cmd_pkg.rc == 0
    assert "openjdk" in cmd_pkg.stdout

    # `java -version` コマンドが正常に実行できること
    cmd_ver = host.run("java -version")
    assert cmd_ver.rc == 0
    # 標準エラーに出力されたバージョン情報の取得
    assert "version" in cmd_ver.stderr or "version" in cmd_ver.stdout
