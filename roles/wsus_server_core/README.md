# Role Name: wsus_server_core

Windows Server Update Services (WSUS) のインストール、WID (Windows Internal Database) の初期化、IIS プールの設定、および定期的なクリーンアップタスクの登録を行います。
本 Role は「Core Role」として機能し、WSUSの基盤構築を担当します。

## Requirements

  * Windows Server 2025
  * Ansible Collection: `ansible.windows`, `community.windows`

## ⚙️ Role Variables

本 Role で定義されている変数は、以下の2種類に分類されます。

1.  **Defaults (`defaults/main.yml`):** ユーザーがオーバーライド可能な基本設定値。
2.  **Internal Vars (`vars/main.yml`):** 内部で使用する定数（通常は変更不要）。

### 1\. User Configurable Variables (defaults/main.yml)

| 変数名 | デフォルト値 | 説明 |
| :--- | :--- | :--- |
| `wsus_server_core_content_dir` | `'C:\WSUS'` | 更新プログラムのコンテンツを保存するローカルディレクトリ |
| `wsus_server_core_features` | `['UpdateServices', ...]` | インストールするWSUS関連機能のリスト |
| `wsus_server_core_service_state` | `started` | WSUSサービスの期待する状態 |
| `wsus_server_core_service_enabled` | `true` | WSUSサービスの自動起動設定 |

### 2\. Internal Constants (vars/main.yml)

| 変数名 | 設定値 | 説明 |
| :--- | :--- | :--- |
| `wsus_server_core_service_name` | `WsusService` | WSUS サービス名 |
| `wsus_server_core_iis_service_name` | `W3SVC` | IIS サービス名 |
| `wsus_server_core_wsusutil_path` | `...` | `wsusutil.exe` への絶対パス |

## 📖 Main Tasks

本 Role は以下のタスクを実行します。

1.  **Install (`01_install.yml`)**: WSUS機能および管理ツールのインストール。
2.  **Post Install (`02_post_install.yml`)**: `wsusutil postinstall` による初期化とサービス起動。
3.  **Configure IIS (`03_configure_iis.yml`)**: `WsusPool` のプライベートメモリ制限を解除 (0に設定) し、クラッシュを防止。
4.  **Schedule Cleanup (`04_schedule_cleanup.yml`)**: 「WSUS Monthly Cleanup」タスクを作成し、毎月1日に不要な更新プログラムやコンピュータの削除を実行。

## 📖 Example Playbook

### 基本的な使用法

Core Role を呼び出し、WSUSをインストールします。

```yaml
- hosts: wsus_servers
  gather_facts: no
  roles:
    - role: my_company.middleware.wsus_server_core
      vars:
        wsus_server_core_content_dir: 'D:\WSUS_Content'
```

## ✅ Quality Assurance

本 Role は以下の動作を保証します。

  * **冪等性:** 複数回実行しても「すでにインストール/設定済み」として扱われ、エラーにならないこと。
  * **初期化:** `wsusutil postinstall` が実行され、指定したコンテンツディレクトリが正しく認識されること。
  * **安定性:** IISの `WsusPool` 設定が最適化され、高負荷時の停止を防ぐ設定が行われること。
