# zabbix_config

Zabbix Server構築完了後に、**Zabbix API**を介して論理的な設定（自動登録ルール、ユーザーグループ、テンプレート適用など）を行うAnsible Role。

## 概要

このRoleは、`zabbix_server_core`とは独立して実行可能で、Zabbix APIを使用して宣言的に監視設定を管理します。
主な機能として、エージェントが起動するだけで自動的に監視が開始される「オートレジストレーション（自動登録）」機能を提供します。

## 特徴

- **API駆動**: 設定ファイルの直接編集ではなく、全てZabbix API経由で設定
- **宣言的管理**: Ansibleの`community.zabbix`コレクションを活用した冪等な設定管理
- **ゼロタッチ・プロビジョニング**: 自動登録設定により、エージェント起動だけで監視開始
- **責務の分離**: インフラ構築（`zabbix_server_core`）とアプリケーション設定（`zabbix_config`）を分離

## Requirements

- Zabbix ServerおよびWeb UIが起動していること
- Ansible実行環境（Controller）にPythonライブラリ`zabbix-api`がインストール可能であること
- `community.zabbix`コレクションがインストールされていること

## Role Variables

### defaults/main.yml

```yaml
# Zabbix API接続情報
zabbix_config_api_url: "http://localhost/zabbix"
zabbix_config_api_user: "Admin"
zabbix_config_api_password: "zabbix"  # Vault等での上書き前提

# 自動登録ルール (Auto Registration)
zabbix_config_autoreg_name: "Auto registration for Linux"
zabbix_config_autoreg_metadata: "Linux"
zabbix_config_autoreg_group: "Linux servers"
zabbix_config_autoreg_template: "Linux by Zabbix agent"

# API接続設定
zabbix_config_api_timeout: 30
zabbix_config_api_validate_certs: false
```

**注意**: `zabbix_config_api_password`はセキュリティ上、本番環境ではAnsible Vault等で暗号化してください。

### 変数の説明

- `zabbix_config_api_url`: Zabbix WebインターフェースのURL
- `zabbix_config_api_user`: API接続用のユーザー名（デフォルトはAdmin）
- `zabbix_config_api_password`: API接続用のパスワード
- `zabbix_config_autoreg_name`: 自動登録アクションの名前
- `zabbix_config_autoreg_metadata`: エージェント側のメタデータとマッチさせる文字列
- `zabbix_config_autoreg_group`: 自動登録時に追加するホストグループ
- `zabbix_config_autoreg_template`: 自動登録時にリンクするテンプレート名

## Dependencies

- `community.zabbix` コレクション (最新版推奨)

## Example Playbook

### 基本的な使用方法

```yaml
- hosts: localhost
  connection: local
  roles:
    - role: middleware.middleware.zabbix_config
      vars:
        zabbix_config_api_url: "http://zabbix-server.example.com/zabbix"
        zabbix_config_api_password: "{{ vault_zabbix_admin_password }}"
```

### zabbix_server_coreと組み合わせた完全な例

```yaml
- hosts: monitoring_servers
  become: true
  tasks:
    # 1. PostgreSQLセットアップ
    - ansible.builtin.include_role:
        name: middleware.middleware.postgresql_core

    # 2. DB作成
    - name: Create Zabbix database
      community.postgresql.postgresql_db:
        name: zabbix
        state: present
      become_user: postgres

    # 3. DBユーザー作成
    - name: Create Zabbix database user
      community.postgresql.postgresql_user:
        db: zabbix
        name: zabbix
        password: "{{ zabbix_db_password }}"
      become_user: postgres

    # 4. Zabbix Serverセットアップ
    - ansible.builtin.include_role:
        name: middleware.middleware.zabbix_server_core
      vars:
        zabbix_server_core_db_password: "{{ zabbix_db_password }}"

    # 5. Zabbix Web UIの起動を待機
    - name: Wait for Zabbix Web UI to be ready
      ansible.builtin.uri:
        url: "http://localhost/zabbix/index.php"
        status_code: 200
      register: result
      until: result.status == 200
      retries: 30
      delay: 5

- hosts: localhost
  connection: local
  tasks:
    # 6. Zabbix設定の適用
    - ansible.builtin.include_role:
        name: middleware.middleware.zabbix_config
      vars:
        zabbix_config_api_url: "http://{{ hostvars[groups['monitoring_servers'][0]]['ansible_host'] }}/zabbix"
        zabbix_config_api_password: "{{ vault_zabbix_admin_password }}"
```

## Testing

```bash
# RHEL 9でテスト
cd roles/zabbix_config
molecule test

# RHEL 8でテスト
MOLECULE_DISTRO=rockylinux8 molecule test
```

## 自動登録の動作確認

このRoleで設定した自動登録を実際に動作させるには、Zabbix Agentに以下の設定を行います：

```ini
# /etc/zabbix/zabbix_agentd.conf
ServerActive=zabbix-server.example.com
HostMetadata=Linux
```

エージェントを起動すると、自動的にZabbix Serverに登録され、`Linux servers`グループに追加され、`Linux by Zabbix agent`テンプレートが適用されます。

## License

MIT

## Author

HyperGenius
