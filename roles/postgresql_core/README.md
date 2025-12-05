# Role Name: postgresql\_core

PostgreSQL データベースサーバーのインストール、初期化、およびベースライン設定を行います。
本 Role は「Core Role」として機能し、プロジェクト固有のチューニング設定を受け入れるための `conf.d` 構造を提供します。

## Requirements

  * RHEL 8 / 9, AlmaLinux, Rocky Linux
  * Ansible Collection: `community.general`

## ⚙️ Role Variables

本 Role で定義されている変数は、以下の2種類に分類されます。

1.  **Defaults (`defaults/main.yml`):** ユーザーがオーバーライド可能な基本設定値。
2.  **Internal Vars (`vars/main.yml`):** OSごとの差異を吸収するための定数（通常は変更不要）。

### 1\. User Configurable Variables (defaults/main.yml)

これらは `group_vars` や Playbook の `vars` で上書きすることを想定したパラメータです。

| 変数名 | デフォルト値 | 説明 |
| :--- | :--- | :--- |
| `postgresql_version` | `"14"` | インストールするPostgreSQLのメジャーバージョン |
| `postgresql_listen_addresses` | `"*"` | 接続を受け付けるIPアドレス（`*` = 全て） |
| `postgresql_port` | `5432` | リッスンポート番号 |
| `postgresql_data_dir` | `/var/lib/pgsql/{{ version }}/data` | データ格納ディレクトリのパス |
| `postgresql_max_connections` | `100` | 最大同時接続数（初期値） |
| `postgresql_global_params` | `{}` | `postgresql.conf` に追記したい任意のパラメータ（辞書形式） |

**⚠️ 副作用についての注意:**
これらのパラメータを変更した場合、反映のために **PostgreSQL サービスの再起動（Restart）** が発生します。

### 2\. Internal Constants (vars/main.yml)

これらは Role 内部で OS の差異（RHEL8系と9系の違いなど）を吸収するために定義されています。
**原則として変更しないでください。** システムの挙動が不安定になる可能性があります。

| 変数名 | RHEL 8 / 9 設定値 | 説明 |
| :--- | :--- | :--- |
| `postgresql_service_name` | `postgresql-{{ version }}` | Systemd サービス名 |
| `postgresql_package_name` | `postgresql{{ version }}-server` | DNF/YUM パッケージ名 |
| `postgresql_bin_dir` | `/usr/pgsql-{{ version }}/bin` | バイナリ格納パス |
| `postgresql_conf_file` | `.../data/postgresql.conf` | 設定ファイルのフルパス |

## 🔧 Extension Mechanism (拡張設定)

本 Role は、プロジェクト固有のチューニング設定を **`conf.d` ディレクトリ** 経由で読み込む設計になっています。
Ansible 変数 (`postgresql_global_params`) にすべてを詰め込むのではなく、設定ファイルとして管理することを推奨します。

### 設定ファイルの配置ルール

  * **ディレクトリ:** `/var/lib/pgsql/{{ version }}/data/conf.d/`
  * **ファイル名:** `*.conf` (例: `99-tuning.conf`)
  * **優先順位:** ファイル名の辞書順で読み込まれるため、プレフィックスに数字をつけることを推奨します（例: `00-base.conf` \< `99-override.conf`）。

## 📖 Example Playbook

### 基本的な使用法

Core Role を呼び出し、その後にプロジェクト固有の設定ファイルを配置します。

```yaml
- hosts: db_servers
  become: true
  
  roles:
    # 1. 基盤設定 (Core Role)
    - role: my_company.middleware.postgresql_core
      vars:
        postgresql_version: "15"
        postgresql_listen_addresses: "*"

  tasks:
    # 2. プロジェクト固有チューニング (Project Config)
    - name: Deploy App Tuning Config
      copy:
        dest: "/var/lib/pgsql/15/data/conf.d/99-app-tuning.conf"
        content: |
          # アプリケーション要件によるチューニング
          work_mem = 16MB
          shared_buffers = 2GB
          maintenance_work_mem = 256MB
          effective_cache_size = 4GB
        owner: postgres
        group: postgres
        mode: '0600'
      notify: Restart Postgres  # postgresql_core Role内のハンドラを呼び出す
```
