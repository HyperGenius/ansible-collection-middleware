def test_postgresql_is_installed(host):
    """PostgreSQLのパッケージがインストールされていることを確認する
    バージョンは変数で指定されたもの（今回はデフォルトの挙動確認のためワイルドカード等で柔軟に）
    """
    p = host.package("postgresql14-server")  # TODO: バージョンを動的に取得する
    assert p.is_installed
