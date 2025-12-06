
# Role Name: nginx\_core

Nginx Webサーバー / リバースプロキシのインストール、初期化、およびセキュリティベースライン設定を行います。
本 Role は「Core Role」として機能し、アプリケーションごとのバーチャルホスト設定を受け入れるための `conf.d` 構造を提供します。

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
| `nginx_version` | `"present"` | パッケージの状態（特定のバージョンを指定したい場合はバージョン番号） |
| `nginx_http_port` | `80` | デフォルトのHTTPリッスンポート |
| `nginx_user` | `nginx` | Nginxワーカープロセスの実行ユーザー |
| `nginx_worker_processes` | `"auto"` | ワーカープロセス数（通常はCPUコア数に合わせるため auto 推奨） |
| `nginx_server_tokens` | `"off"` | セキュリティ設定：バージョン情報の隠蔽（off推奨） |
| `nginx_client_max_body_size` | `"1m"` | アップロード可能な最大ファイルサイズ |
| `nginx_keepalive_timeout` | `"65"` | KeepAlive タイムアウト秒数 |
| `nginx_global_params` | `{}` | `nginx.conf` の `http` ブロックに追記したい任意のパラメータ |

**⚠️ 副作用についての注意:**
これらのパラメータを変更した場合、反映のために **Nginx サービスの再起動（Restart）またはリロード（Reload）** が発生します。

### 2\. Internal Constants (vars/main.yml)

これらは Role 内部で OS の差異を吸収するために定義されています。
**原則として変更しないでください。**

| 変数名 | RHEL 8 / 9 設定値 | 説明 |
| :--- | :--- | :--- |
| `nginx_service_name` | `nginx` | Systemd サービス名 |
| `nginx_conf_dir` | `/etc/nginx` | 設定ディレクトリのルート |
| `nginx_conf_file` | `/etc/nginx/nginx.conf` | メイン設定ファイルのパス |
| `nginx_conf_d_dir` | `/etc/nginx/conf.d` | 拡張設定ディレクトリ |

## 🔧 Extension Mechanism (拡張設定)

本 Role は、プロジェクト固有のバーチャルホスト設定（Server Block）を **`conf.d` ディレクトリ** 経由で読み込む設計になっています。
Ansible 変数で複雑な `location` 設定を管理しようとせず、設定ファイルとして管理することを強く推奨します。

### 設定ファイルの配置ルール

  * **ディレクトリ:** `/etc/nginx/conf.d/`
  * **ファイル名:** `*.conf` (例: `app_proxy.conf`)
  * **優先順位:** アルファベット順で読み込まれます。`default.conf` を無効化したい場合は、同名のファイルを上書きするか削除してください。

## 📖 Example Playbook

### 基本的な使用法

Core Role を呼び出し、その後にプロジェクト固有のリバースプロキシ設定などを配置します。

```yaml
- hosts: web_servers
  become: true
  
  roles:
    # 1. 基盤設定 (Core Role)
    - role: my_company.middleware.nginx_core
      vars:
        # アップロード要件があるため、ここだけ緩める
        nginx_client_max_body_size: "10m"
        nginx_server_tokens: "off"

  tasks:
    # 2. プロジェクト固有設定 (Project Config)
    # バーチャルホストやリバースプロキシ設定を配置する
    - name: Deploy Application Proxy Config
      copy:
        dest: "/etc/nginx/conf.d/my_app.conf"
        content: |
          server {
              listen 80;
              server_name app.example.com;

              location / {
                  proxy_pass http://localhost:8080;
                  proxy_set_header Host $host;
                  proxy_set_header X-Real-IP $remote_addr;
              }
          }
        owner: root
        group: root
        mode: '0644'
      # nginx_core Role内のハンドラを呼び出して設定を反映させる
      notify: Reload Nginx
```

## ✅ Quality Assurance (Test Strategy)

本 Role は Molecule により以下の品質が担保されています。

  * **構文チェック:** 生成された設定ファイルが `nginx -t` をパスすること。
  * **ポート確認:** 指定したポート（デフォルト80）で Listen していること。
  * **拡張性:** `conf.d` に配置した設定ファイルが正しく読み込まれること。
