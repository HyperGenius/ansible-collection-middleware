def test_extension_mechanism(host, postgresql_vars):
    """PostgreSQLの拡張ディレクトリパターンが機能していることを確認する"""
    base_dir = postgresql_vars["data_dir"]
    conf_d = host.file(f"{base_dir}/conf.d")

    # conf.dディレクトリの確認
    assert conf_d.exists
    assert conf_d.is_directory

    # include_dirの確認
    postgresql_conf = host.file(f"{base_dir}/postgresql.conf")
    assert postgresql_conf.contains("include_dir = 'conf.d'")
