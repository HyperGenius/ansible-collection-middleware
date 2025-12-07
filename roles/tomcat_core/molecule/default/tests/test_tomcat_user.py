def test_tomcat_user(host, tomcat_vars):
    """tomcat ユーザーが存在すること"""
    tomcat_user = tomcat_vars["tomcat_user"]
    tomcat_group = tomcat_vars["tomcat_group"]

    user = host.user(tomcat_user)
    assert user.exists

    # tomcat グループが存在すること
    group = host.group(tomcat_group)
    assert group.exists
    assert user.group == group.name

    # tomcat ユーザーのホームディレクトリが適切であること
    assert user.home in ["/home/tomcat", "/opt/tomcat"]

    # シェルが /sbin/nologin であること
    assert user.shell == "/sbin/nologin"
