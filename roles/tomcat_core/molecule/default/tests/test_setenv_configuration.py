def test_setenv_configuration(host, tomcat_vars):
    """bin/setenv.sh ファイルが存在すること"""
    env_dir = tomcat_vars["tomcat_core_install_dir"]
    setenv = host.file(f"{env_dir}/bin/setenv.sh")
    assert setenv.exists
    assert setenv.is_file

    # --- setenv.sh が正しく読み込まれているか検証 ---
    # tomcatユーザーで実行されているjavaプロセスを取得
    tomcat_processes = host.process.filter(user="tomcat", comm="java")

    # プロセスが少なくとも1つ存在すること
    assert len(tomcat_processes) > 0

    # いずれかのプロセスにヒープ設定が含まれていることを確認
    found_settings = False
    for p in tomcat_processes:
        if "-Xms" in p.args and "-Xmx" in p.args:
            found_settings = True
            break

    assert found_settings
