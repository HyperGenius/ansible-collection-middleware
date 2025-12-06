def test_extension_mechanism(host, nginx_vars):
    """conf.dの読み込み設定が有効か確認"""
    conf_file = nginx_vars["nginx_conf_file"]
    conf_d_dir = nginx_vars["nginx_conf_d_dir"]

    f = host.file(conf_file)
    assert f.exists

    # ワイルドカードを含むinclude設定が存在するか
    expected = f"include {conf_d_dir}/*.conf;"
    assert expected in f.content.decode("utf-8")
