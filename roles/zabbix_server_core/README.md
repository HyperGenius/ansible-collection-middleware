# zabbix_server_core

統合監視マネージャである **Zabbix Server (PostgreSQL版)** を構築するAnsible Role。

## 概要

このRoleは、Zabbix Serverプロセスの構築に専念します。
データベース（PostgreSQL）やWebサーバー（Nginx）は、別Role（`postgresql_core`, `nginx_core`）または別サーバーにあることを前提とします。

## 特徴

- **コンポーネントの分離**: Zabbix Serverプロセスのみを管理
- **自動DBスキーマ投入**: 初期構築時にZabbix配布の巨大なSQL (`server.sql.gz`) を自動でインポート
- **冪等性**: すでにデータがある場合はスキーマ投入をスキップ
- **機密情報の分離**: `DBPassword` などの機密情報は `conf.d` パターンで別ファイルに配置

## Requirements

- PostgreSQL 12以降がインストールされていること
- Zabbix用のデータベースとユーザーが作成されていること

## Role Variables

### defaults/main.yml

```yaml
zabbix_server_core_version: "6.0"              # Zabbixメジャーバージョン
zabbix_server_core_db_host: "localhost"         # DB接続先
zabbix_server_core_db_name: "zabbix"            # DB名
zabbix_server_core_db_user: "zabbix"            # DBユーザー名
zabbix_server_core_listen_port: 10051           # リッスンポート
```

**注意**: `zabbix_server_core_db_password` はセキュリティ上、デフォルトでは定義されていません。
プロジェクト側で注入するか、`/etc/zabbix/zabbix_server.conf.d/` に別ファイルとして配置してください。

## Dependencies

なし

## Example Playbook

```yaml
- hosts: monitoring_servers
  become: true
  roles:
    # 1. PostgreSQLをセットアップ
    - role: middleware.middleware.postgresql_core
      vars:
        postgresql_core_version: "14"
    
    # 2. Zabbix用のDBとユーザーを作成（例）
    # ... community.postgresql モジュールを使用 ...
    
    # 3. DBパスワード設定ファイルを作成
    - name: Create DBPassword configuration
      copy:
        content: |
          DBPassword=your_secure_password
        dest: /etc/zabbix/zabbix_server.conf.d/dbpassword.conf
        owner: zabbix
        group: zabbix
        mode: '0640'
    
    # 4. Zabbix Serverをセットアップ
    - role: middleware.middleware.zabbix_server_core
      vars:
        zabbix_server_core_version: "6.0"
        zabbix_server_core_db_password: "your_secure_password"
```

## Testing

```bash
# RHEL 9でテスト
cd roles/zabbix_server_core
molecule test

# RHEL 8でテスト
MOLECULE_DISTRO=rockylinux8 molecule test
```

## License

MIT

## Author

HyperGenius
