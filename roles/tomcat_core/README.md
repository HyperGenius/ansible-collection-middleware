# Role Name: tomcat_core

Apache Tomcat (tarball) のインストール、Java (OpenJDK) のセットアップ、および初期設定を行う Ansible Role です。
本 Role は「Core Role」として機能し、アプリケーションごとの環境変数を注入するための `setenv.d` 拡張ディレクトリを提供します。

## Requirements

* RHEL 8 / 9, AlmaLinux, Rocky Linux
* Ansible Collection: `community.general`

## ⚙️ Role Variables

本 Role で定義されている変数は、`defaults/main.yml` で定義されており、オーバーライド可能です。
変数名はすべて `tomcat_core_` プレフィックスを持ちます。

### 基本設定

| 変数名 | デフォルト値 | 説明 |
| :--- | :--- | :--- |
| `tomcat_core_version` | `"10.1.49"` | インストールする Tomcat のバージョン |
| `tomcat_core_java_version` | `"11"` | インストールする OpenJDK のバージョン (例: 11, 17) |
| `tomcat_core_http_port` | `8080` | HTTP リッスンポート |
| `tomcat_core_shutdown_port` | `8005` | シャットダウンポート |
| `tomcat_core_ajp_port` | `8009` | AJP ポート |
| `tomcat_core_user` | `tomcat` | Tomcat プロセスの実行ユーザー |
| `tomcat_core_group` | `tomcat` | Tomcat プロセスの実行グループ |

### メモリ・JVM設定 (setenv.sh)

`bin/setenv.sh` に反映される設定値です。

| 変数名 | デフォルト値 | 説明 |
| :--- | :--- | :--- |
| `tomcat_core_heap_min` | `"512m"` | 初期のヒープサイズ (-Xms) |
| `tomcat_core_heap_max` | `"1024m"` | 最大ヒープサイズ (-Xmx) |
| `tomcat_core_java_opts` | `"-Djava.awt.headless=true"` | その他の JAVA_OPTS オプション |

## 📂 Directories & Paths

本 Role は以下のパス構成でインストールを行います。

| パス | 値 (デフォルト) | 説明 |
| :--- | :--- | :--- |
| インストール先 | `/opt/tomcat` | `/opt/apache-tomcat-X.Y.Z` へのシンボリックリンク |
| 設定ディレクトリ | `/opt/tomcat/conf` | `server.xml` 等の配置場所 |
| 拡張設定配置先 | `/opt/tomcat/bin/setenv.d/` | ユーザー定義の環境変数スクリプト配置先 |

## 🔧 Extension Mechanism (拡張設定)

本 Role は、`setenv.sh` を Ansible で管理します。ユーザーが独自の環境変数を追加したい場合は、**`setenv.d` ディレクトリ** を使用してください。

### setenv.sh の管理方針

* **基本設定:** `tomcat_core_heap_min` などの変数を使用してください。`setenv.sh` 自体は上書きしないでください。
* **追加設定:** `/opt/tomcat/bin/setenv.d/` ディレクトリ配下に `.sh` ファイルを配置すると、Tomcat 起動時に自動的に読み込まれます。

## 📖 Example Playbook

### 基本的な使用法

Core Role を呼び出し、その後にプロジェクト固有の設定ファイル（`setenv.d` 配下）を配置します。

```yaml
- hosts: app_servers
  become: true
  
  vars:
    # バージョンやポートの指定
    tomcat_core_version: "10.1.49"
    tomcat_core_java_version: "17"
    tomcat_core_http_port: 8080
    
    # 基本的なメモリ設定
    tomcat_core_heap_min: "1024m"
    tomcat_core_heap_max: "2048m"

  roles:
    - role: middleware.middleware.tomcat_core

  tasks:
    # アプリケーション固有のシステムプロパティなどを追加
    - name: Deploy App Specific Env Config
      copy:
        dest: "/opt/tomcat/bin/setenv.d/99-app-env.sh"
        content: |
          #!/bin/sh
          export JAVA_OPTS="$JAVA_OPTS -Dapp.env=production -Ddb.url=jdbc:mysql://db:3306/mydb"
        owner: tomcat
        group: tomcat
        mode: '0750'
      notify: Restart Tomcat

  handlers:
    - name: Restart Tomcat
      ansible.builtin.service:
        name: tomcat
        state: restarted
```

## 🏗 Architecture Decision Records (ADR)

本 Role の設計意思と理由は以下の通りです。

### 1. インストール方式: OSパッケージではなくアーカイブ(tar.gz)を採用

* **Context:** RHEL/Rocky Linux 標準リポジトリの Tomcat はバージョンが古い場合が多く、Jakarta EE 対応の Tomcat 10系など、最新機能が必要なプロジェクト要件を満たせないことが多い。
* **Decision:** Apache Tomcat 公式配布の `tar.gz` を `/opt` 配下に展開する方式を採用した。
* **Consequence:**
    * 任意のマイナーバージョンを指定してインストール可能になった。
    * Systemd ユニットファイルやユーザー作成を Role 側で管理する必要が生じたが、これにより構成の完全な制御が可能になった。

### 2. 設定管理: `setenv.d` ディレクトリパターンによる拡張

* **Context:** Tomcat の環境変数は通常 `bin/setenv.sh` 単一ファイルで管理される。しかし、インフラ設定（メモリ等のJVM設定）とアプリケーション固有設定（DB接続情報やプロファイル指定）が混在し、デプロイメントパイプラインでの管理が複雑になりがちである。
* **Decision:** `setenv.sh` 内で、カスタムディレクトリ `bin/setenv.d/*.sh` をループして読み込むロジックを実装した。
* **Consequence:**
    * **責務の分離:** 本 Role は「インフラとしてのベース設定（ヒープサイズ等）」のみを管理し、アプリケーション固有の変数は別ファイルとしてデプロイ時に追加配置することが可能になった。
    * **IaCの安全性:** `setenv.sh` 自体を書き換えることなく設定を追加できるため、Ansible 実行による意図しない設定上書きを防げる。

### 3. バージョン管理: `JAVA_HOME` の動的解決

* **Context:** Java のマイナーバージョンアップによりディレクトリパス（例: `/usr/lib/jvm/java-11-openjdk-11.0.12...`）が変わることがあり、パスのハードコードは保守性を下げる。
* **Decision:** `ansible.builtin.find` モジュールを使用して、インストールされている Java バージョンに対応するディレクトリを動的に特定し、Systemd の環境変数として埋め込む方式を採用した。
* **Consequence:** Java パッケージのマイナーアップデートがあっても、Role を再実行するだけで新しいパスが Systemd に反映される堅牢性が確保された。

### 4. 変数スコープ: `tomcat_core_` プレフィックスの採用

* **Context:** Ansible の変数はフラットな名前空間を持つため、単に `tomcat_port` とすると、他の Tomcat 関連 Role やアプリケーション Role と競合するリスクがある。
* **Decision:** 全ての変数に `tomcat_core_` プレフィックスを付与した。
* **Consequence:** 変数名が長くなるが、変数の所属が明確になり、大規模な Playbook においても安全に利用できる。
