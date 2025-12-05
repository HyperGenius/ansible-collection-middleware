# Ansible Collection: middleware

標準的なミドルウェア構築用AnsibleCollectionです。

PostgreSQL, Nginx, Tomcatなどの主要ミドルウェアについて、セキュリティと品質が担保されたCore Roleを提供します。

## 🎯 設計思想 (Design Philosophy)

本コレクションのRoleは、以下の設計方針に基づいて開発されています。

1.  **Core / Project 分離モデル**
      * **Core Role:** インストール、自動起動設定、ログ設定、ディレクトリ構造の維持など、「基盤として変わらない部分」を管理
      * **Project Config:** アプリケーション固有のチューニング（メモリ設定、接続数など）は利用側で管理
2.  **設定ディレクトリ (conf.d) パターン**
      * 巨大な設定ファイル（`postgresql.conf` 等）を直接編集するのではなく`conf.d/` 配下に設定ファイルを配置する方式を採用
      * これによりAnsible変数の競合を防ぎ、設定の可読性向上を期待

## 📦 収録 Roles

| Role名 | バージョン | 説明 | 拡張ポイント |
| :--- | :--- | :--- | :--- |
| `postgresql_core` | 13, 14, 15 | PostgreSQL データベースサーバー | `conf.d/*.conf` |
| `nginx_core` | 1.20+ | Webサーバー / リバースプロキシ | `conf.d/*.conf`, `default.d/*.conf` |
| `tomcat_core` | 9.0+ | Java アプリケーションサーバー | `setenv.sh` |

*(※ 今後追加予定のミドルウェアもここに記載します)*

## 🚀 インストール方法

`requirements.yml`から読み込める場合は次を記述してインストールしてください。

```yaml
collections:
  - name: git+ssh://git@github.com/<Path to repository>/middleware.git
    version: "1.0.0"  # 使用するバージョンを固定することを推奨
```

インストールコマンド:

```bash
ansible-galaxy collection install -r requirements.yml
```

## 📖 利用方法 (Usage)

### 基本的な使い方（デフォルト設定）

標準的な設定で起動するだけであれば、変数はほとんど不要です。

```yaml
- hosts: db_servers
  roles:
    - role: my_company.middleware.postgresql_core
      vars:
        postgresql_version: "14"
```

### プロジェクト固有のチューニングを行う場合

各Roleは「拡張用ディレクトリ」を読み込むように設定されています。
アプリ固有の設定値は、`copy` モジュール等でファイルを配置してください。

**Playbook例:**

```yaml
- hosts: db_servers
  roles:
    # 1. 基盤設定 (Core Role)
    - role: middleware.postgresql_core
      vars:
        postgresql_version: "14"

  tasks:
    # 2. アプリ固有設定 (Project Config)
    # Core Roleが作成した conf.d ディレクトリに配置する
    - name: Deploy Project Tuning Config
      copy:
        dest: /var/lib/pgsql/data/conf.d/99-app-tuning.conf
        content: |
          # アプリケーション要件によるチューニング
          max_connections = 200
          work_mem = 16MB
          shared_buffers = 1GB
      notify: Restart Postgres  # ハンドラ名は各Roleのドキュメント参照
```

## ✅ 品質保証 (Quality Assurance)

本コレクションに含まれる Role は、**Molecule** および **Testinfra** を用いた自動テストにより、以下の項目が保証されています。

  * **冪等性 (Idempotence):** 何度実行しても設定が壊れないこと。
  * **副作用の検証:** 設定変更時にプロセスが正しく再起動/リロードされること。
  * **セキュリティ:** 不要なポートが閉じており、適切な権限設定がなされていること。

## 🤝 開発者向け (Contribution)

### テストの実行

開発には Molecule を使用します。

```bash
# 依存関係のインストール
pip install molecule "molecule-plugins[docker]" requests<2.32.0

# テスト実行
cd roles/postgresql_core
molecule test
```
