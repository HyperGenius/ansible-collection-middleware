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
以下のいずれかの方法で設定してください：

1. **Ansible変数として渡す**（簡易的な方法、テスト用）:
   ```yaml
   vars:
     zabbix_server_core_db_password: "your_password"
   ```
   この場合、Role が自動的に `/etc/zabbix/zabbix_server.conf.d/dbpassword.conf` を作成します。

2. **プロジェクト側でファイルを配置**（推奨、本番環境向け）:
   `/etc/zabbix/zabbix_server.conf.d/` に独自のファイルを作成し、パスワードを含めます。

## Dependencies

なし

## Example Playbook

### Method 1: Using Ansible Variable (Simpler, for testing)

```yaml
- hosts: monitoring_servers
  become: true
  roles:
    # 1. PostgreSQLをセットアップ
    - role: middleware.middleware.postgresql_core
      vars:
        postgresql_core_version: "14"
    
    # 2. Zabbix用のDBとユーザーを作成
    - name: Create Zabbix database and user
      block:
        - community.postgresql.postgresql_db:
            name: zabbix
            encoding: UTF-8
          become_user: postgres
        
        - community.postgresql.postgresql_user:
            db: zabbix
            name: zabbix
            password: your_secure_password
          become_user: postgres
    
    # 3. Zabbix Serverをセットアップ（パスワードは変数で渡す）
    - role: middleware.middleware.zabbix_server_core
      vars:
        zabbix_server_core_version: "6.0"
        zabbix_server_core_db_password: "your_secure_password"
```

### Method 2: Using conf.d File (Recommended for production)

```yaml
- hosts: monitoring_servers
  become: true
  tasks:
    # 1. PostgreSQLをセットアップ
    - ansible.builtin.include_role:
        name: middleware.middleware.postgresql_core
      vars:
        postgresql_core_version: "14"
    
    # 2. Zabbix用のDBとユーザーを作成
    # ... (省略)
    
    # 3. Zabbix Serverをセットアップ（パスワードはまだ設定しない）
    - ansible.builtin.include_role:
        name: middleware.middleware.zabbix_server_core
      vars:
        zabbix_server_core_version: "6.0"
        # パスワードは渡さない - 次のタスクでファイルとして配置
    
    # 4. DBパスワード設定ファイルを作成（プロジェクト管理）
    - name: Create DBPassword configuration
      ansible.builtin.copy:
        content: |
          DBPassword=your_secure_password
        dest: /etc/zabbix/zabbix_server.conf.d/dbpassword.conf
        owner: zabbix
        group: zabbix
        mode: '0640'
      notify: Restart Zabbix Server
  
  handlers:
    - name: Restart Zabbix Server
      ansible.builtin.service:
        name: zabbix-server
        state: restarted
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
