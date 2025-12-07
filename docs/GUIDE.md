# Middleware Collection Usage Guide

このドキュメントでは、本コレクション（`middleware-collection`）を使用して、実際のプロジェクトにミドルウェアを導入・構築するための標準フローとベストプラクティスについて解説します。

## 🎯 1. Core Concept (設計思想)

本コレクションは **「Core Role パターン」** を採用しています。これは、インフラ設定を「不変な基盤部分」と「プロジェクト固有の可変部分」に分離する設計です。

| レイヤー | 役割 (Role) | 責務 | 管理リポジトリ |
| :--- | :--- | :--- | :--- |
| **Layer 1** | **Core Roles** | ミドルウェアのインストール、初期化、セキュリティベースライン設定、起動管理 | `middleware-collection` (本リポジトリ) |
| **Layer 2** | **Project Roles** | アプリケーション固有のチューニング、環境変数、DBスキーマ、バーチャルホスト設定 | 各プロジェクトのリポジトリ |

**原則:** 利用者は Core Role のタスクを直接修正してはいけません。Core Role が提供する「拡張ポイント（設定ファイル配置ディレクトリなど）」を利用して設定を注入します。

## 📦 2. Repository Structure (リポジトリ構成)

プロジェクトでの利用時は、以下のようにリポジトリを分離することを強く推奨します。

```text
[Repo A: middleware-collection] (Provider)
   ├── roles/
   │    ├── tomcat_core/      # v1.0.0
   │    ├── postgresql_core/  # v1.0.0
   │    └── nginx_core/       # v1.0.0
   └── (Tagged Releases)

        ⬇️ (Reference via requirements.yml)

[Repo B: your-project-deploy] (Consumer)
   ├── requirements.yml       # 使用するCoreのバージョンを固定
   ├── site.yml               # Playbook
   └── roles/
        └── my_app_config/    # プロジェクト固有設定
             ├── templates/
             │    ├── setenv-app.sh.j2
             │    └── my-app.conf.j2
             └── tasks/
                  └── main.yml
```

## 🚀 3. Workflow (導入フロー)

### Step 1: 依存関係の定義 (`requirements.yml`)

プロジェクトリポジトリの `requirements.yml` で、使用するコレクションのバージョンを**タグ指定**で固定します。これにより、基盤側の変更による予期せぬ影響を防ぎます。

```yaml
# project-repo/requirements.yml
collections:
  - name: git+ssh://git@github.com/my-company/middleware-collection.git
    type: git
    version: "v1.2.0"  # ⚠️ Always pin the version tag!
```

### Step 2: Playbook の作成 (`site.yml`)

Core Role を先に実行し、その後にプロジェクト固有の設定 Role を実行する順序で記述します。

```yaml
# project-repo/site.yml
- name: Setup Application Server
  hosts: app_servers
  become: true
  
  roles:
    # 1. 基盤の構築 (Core Role)
    - role: middleware.middleware.tomcat_core
      vars:
        tomcat_core_version: "10.1.49"
        tomcat_core_heap_min: "2048m"

    # 2. アプリ固有設定の適用 (Project Role)
    - role: my_app_tomcat_config
```

### Step 3: 設定の注入 (Extension Pattern)

各 Core Role は、設定を外部から注入するためのディレクトリ（拡張ポイント）を提供しています。プロジェクト用 Role では、そこにファイルを配置するだけで設定が反映されます。

#### 🔹 Tomcat Core の場合

  * **拡張ポイント:** `/opt/tomcat/bin/setenv.d/*.sh`
  * **用途:** 環境変数、JVMオプション (`JAVA_OPTS`)、システムプロパティ

<!-- end list -->

```yaml
# roles/my_app_tomcat_config/tasks/main.yml
- name: Deploy App Environment Config
  ansible.builtin.template:
    src: app-env.sh.j2
    dest: /opt/tomcat/bin/setenv.d/99-app-env.sh
    owner: tomcat
    group: tomcat
    mode: '0750'
  notify: Restart Tomcat  # Core Roleが提供するハンドラを呼ぶ
```

#### 🔹 Nginx Core の場合 (例)

  * **拡張ポイント:** `/etc/nginx/conf.d/*.conf`
  * **用途:** バーチャルホスト設定、リバースプロキシ設定

<!-- end list -->

```yaml
# roles/my_app_nginx_config/tasks/main.yml
- name: Deploy VirtualHost Config
  ansible.builtin.template:
    src: my-app.conf.j2
    dest: /etc/nginx/conf.d/my-app.conf
  notify: Reload Nginx
```

#### 🔹 PostgreSQL Core の場合 (例)

  * **拡張ポイント:** `/var/lib/pgsql/data/conf.d/*.conf`
  * **用途:** `work_mem`, `max_connections` 等のチューニング

<!-- end list -->

```yaml
# roles/my_app_db_config/tasks/main.yml
- name: Deploy DB Tuning
  ansible.builtin.template:
    src: tuning.conf.j2
    dest: /var/lib/pgsql/data/conf.d/99-tuning.conf
  notify: Restart PostgreSQL
```

## ✅ Best Practices

1.  **バージョン固定の徹底:**
      * `requirements.yml` で `version: main` や `master` を指定しないでください。「朝起きたらデプロイが失敗する」原因になります。
2.  **Core Role をラップする:**
      * 機能が不足している場合でも、Core Role を直接編集せず、Wrapper Role (Project Role) で補うか、Core Role へのプルリクエストを作成して機能を汎用化してください。
3.  **ハンドラの再利用:**
      * 設定ファイルを配置した後は、必ずサービスの再起動が必要です。各 Core Role は `Restart Tomcat` や `Restart Nginx` といったハンドラを公開しているため、Project Role から `notify` で呼び出してください。

## 🔄 Upgrade Guide (バージョンアップ手順)

Middleware Collection の新しいバージョンを取り込む際の手順です。

1.  **Release Note の確認:** `middleware-collection` の更新履歴を確認し、Breaking Changes (破壊的変更) がないか確認します。
2.  **Version の更新:** プロジェクト側の `requirements.yml` のバージョン番号を書き換えます。
3.  **テスト実行:** Molecule テスト、または開発環境への適用を行い、動作を確認します。
4.  **本番適用:** 問題なければ本番環境へデプロイします。
