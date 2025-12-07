def test_tomcat_structure(host, tomcat_vars):
    """インストールディレクトリ (/opt/tomcat) が存在し、ディレクトリであること"""
    tomcat_core_install_dir = tomcat_vars["tomcat_core_install_dir"]
    tomcat_core_user = tomcat_vars["tomcat_core_user"]
    tomcat_core_group = tomcat_vars["tomcat_core_group"]

    tomcat_home_file = host.file(tomcat_core_install_dir)
    assert tomcat_home_file.exists

    # リンクの場合はリンク先を確認する
    if tomcat_home_file.is_symlink:
        tomcat_home_file = host.file(tomcat_home_file.linked_to)

    assert tomcat_home_file.is_directory

    # ディレクトリの所有者が tomcat:tomcat であること
    assert tomcat_home_file.user == tomcat_core_user
    assert tomcat_home_file.group == tomcat_core_group

    target_subdirs = ["bin", "conf", "lib", "logs", "webapps"]

    # 主要ディレクトリ (bin, conf, lib, logs, webapps) が存在すること
    for subdir in target_subdirs:
        target_d = host.file(f"{tomcat_core_install_dir}/{subdir}")
        assert target_d.exists
        assert target_d.is_directory
        assert target_d.user == tomcat_core_user
        assert target_d.group == tomcat_core_group
