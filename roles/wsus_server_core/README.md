# Role Name: wsus_server_core

Windows Server Update Services (WSUS) のインストール、WID (Windows Internal Database) の初期化、およびサービス管理を行います。
本 Role は「Core Role」として機能し、WSUSの基盤構築を担当します。

## Requirements

  * Windows Server 2016 / 2019 / 2022
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

### 2\. Internal Constants (vars/main.yml)

| 変数名 | 設定値 | 説明 |
| :--- | :--- | :--- |
| `wsus_server_core_service_name` | `WsusService` | WSUS サービス名 |
| `wsus_server_core_wsusutil_path` | `...` | `wsusutil.exe` への絶対パス |

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
