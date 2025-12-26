# Zabbix Agent Core ロール

Linux (RHEL系) および Windows Server 向けのクロスプラットフォーム Zabbix Agent 2 インストールおよび設定ロール。

## 概要

このロールは、Linux および Windows システムの両方に Zabbix Agent 2 (Go ベースのエージェント) をインストールおよび設定します。以下のベースライン設定を提供します:

- 公式 Zabbix リポジトリからのインストール
- Zabbix Server への自動登録
- `conf.d` パターンによる拡張設定 (Linux)
- ファイアウォール設定

## サポートされるプラットフォーム

### Linux
- RHEL 8, 9
- AlmaLinux 8, 9
- Rocky Linux 8, 9

### Windows
- Windows Server 2019
- Windows Server 2022
- Windows Server 2025

## 要件

### Linux
- Ansible 2.9 以上
- `ansible.posix` コレクション (firewalld モジュール用)

### Windows
- Ansible 2.9 以上
- `ansible.windows` コレクション
- `community.windows` コレクション

## ロール変数

### コア設定

| 変数 | デフォルト | 説明 |
|----------|---------|-------------|
| `zabbix_agent_core_version` | `"7.0"` | インストールする Zabbix のメジャーバージョン |
| `zabbix_agent_core_server` | `"127.0.0.1"` | パッシブチェック用の Zabbix サーバー IP |
| `zabbix_agent_core_server_active` | `"127.0.0.1"` | アクティブチェック用の Zabbix サーバー IP |
| `zabbix_agent_core_hostname` | `{{ inventory_hostname }}` | Zabbix 上でのホスト名 |
| `zabbix_agent_core_host_metadata` | `"Linux"` または `"Windows"` | 自動登録用のホストメタデータ |
| `zabbix_agent_core_listen_port` | `10050` | パッシブチェック用のリッスンポート |

### Linux 固有の変数

| 変数 | デフォルト | 説明 |
|----------|---------|-------------|
| `zabbix_agent_core_config_file_linux` | `/etc/zabbix/zabbix_agent2.conf` | 設定ファイルのパス |
| `zabbix_agent_core_include_dir` | `/etc/zabbix/zabbix_agent2.d` | 追加設定用のディレクトリ |
| `zabbix_agent_core_log_file_linux` | `/var/log/zabbix/zabbix_agent2.log` | ログファイルのパス |
| `zabbix_agent_core_service_name_linux` | `zabbix-agent2` | サービス名 |

### Windows 固有の変数

| 変数 | デフォルト | 説明 |
|----------|---------|-------------|
| `zabbix_agent_core_windows_version` | `"7.0.6"` | 正確な Windows インストーラーのバージョン |
| `zabbix_agent_core_config_file_windows` | `C:\Program Files\Zabbix Agent 2\zabbix_agent2.conf` | 設定ファイルのパス |
| `zabbix_agent_core_log_file_windows` | `C:\Program Files\Zabbix Agent 2\zabbix_agent2.log` | ログファイルのパス |
| `zabbix_agent_core_service_name_windows` | `Zabbix Agent 2` | サービス名 |

### その他の変数

| 変数 | デフォルト | 説明 |
|----------|---------|-------------|
| `zabbix_agent_core_configure_firewall` | `true` | ファイアウォールルールを設定するかどうか |
| `zabbix_agent_core_service_state` | `started` | サービスの希望する状態 |
| `zabbix_agent_core_service_enabled` | `true` | 起動時にサービスを有効にするかどうか |

## 依存関係

なし。

## プレイブックの例

### 基本的な使用法 (Linux)

```yaml
- hosts: linux_servers
  become: true
  roles:
    - role: middleware.middleware.zabbix_agent_core
      vars:
        zabbix_agent_core_server: "192.168.1.100"
        zabbix_agent_core_server_active: "192.168.1.100"
        zabbix_agent_core_hostname: "{{ inventory_hostname }}"
```

### 基本的な使用法 (Windows)

```yaml
- hosts: windows_servers
  roles:
    - role: middleware.middleware.zabbix_agent_core
      vars:
        zabbix_agent_core_server: "192.168.1.100"
        zabbix_agent_core_server_active: "192.168.1.100"
        zabbix_agent_core_hostname: "{{ inventory_hostname }}"
```

### 高度な設定 (カスタムパラメータを使用した Linux)

```yaml
- hosts: linux_servers
  become: true
  roles:
    - role: middleware.middleware.zabbix_agent_core
      vars:
        zabbix_agent_core_server: "192.168.1.100"
        zabbix_agent_core_server_active: "192.168.1.100"
        zabbix_agent_core_host_metadata: "Linux DB Production"

  tasks:
    # エージェントインストール後にカスタム UserParameter を追加
    - name: Deploy custom monitoring parameters
      ansible.builtin.copy:
        dest: /etc/zabbix/zabbix_agent2.d/custom-monitoring.conf
        content: |
          # Custom monitoring parameters
          UserParameter=custom.check,/usr/local/bin/custom_check.sh
        owner: zabbix
        group: zabbix
        mode: '0640'
      notify: Restart Zabbix Agent 2
```

## 拡張性

### Linux: conf.d パターン

このロールは、追加の設定ファイル用にインクルードディレクトリ (`/etc/zabbix/zabbix_agent2.d/`) を作成します。このディレクトリに `.conf` ファイルを配置することで、カスタム `UserParameter` 定義、TLS 設定、その他の設定をデプロイできます。

プロジェクト固有のロールの例:

```yaml
# roles/my_app_monitoring/tasks/main.yml
- name: Deploy application-specific monitoring
  ansible.builtin.template:
    src: app-monitoring.conf.j2
    dest: /etc/zabbix/zabbix_agent2.d/99-app-monitoring.conf
    owner: zabbix
    group: zabbix
    mode: '0640'
  notify: Restart Zabbix Agent 2
```

## ハンドラー

このロールは以下のハンドラーを提供します:

- `Restart Zabbix Agent 2` - Zabbix Agent 2 サービスを再起動します (Linux)
- `Restart Zabbix Agent 2 (Windows)` - Zabbix Agent 2 サービスを再起動します (Windows)

## テスト

### Molecule (Linux)

このロールには Linux プラットフォーム用の Molecule テストが含まれています:

```bash
cd roles/zabbix_agent_core
molecule test
```

異なるディストリビューションでテストするには:

```bash
MOLECULE_DISTRO=rockylinux9 molecule test
MOLECULE_DISTRO=rockylinux8 molecule test
```

## ライセンス

MIT

## 著者情報

HyperGenius
