def test_nginx_user_and_group(host, nginx_vars):
    """Nginx実行ユーザーとグループの確認"""
    user_name = nginx_vars["nginx_user"]
    user = host.user(user_name)
    assert user.exists
    assert user.group == user_name


def test_nginx_user_id(host, nginx_vars):
    """Nginx実行ユーザーのUIDの確認, 定義されている場合のみ実行"""
    nginx_uid = nginx_vars.get("nginx_uid", None)

    if nginx_uid:
        user_name = nginx_vars["nginx_user"]
        user = host.user(user_name)
        assert user.uid == nginx_uid


def test_nginx_group_id(host, nginx_vars):
    """Nginx実行ユーザーのGIDの確認, 定義されている場合のみ実行"""
    nginx_gid = nginx_vars.get("nginx_gid", None)

    if nginx_gid:
        user_name = nginx_vars["nginx_user"]
        user = host.user(user_name)
        assert user.gid == nginx_gid
