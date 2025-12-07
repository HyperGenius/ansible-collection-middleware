# Role Name: tomcat\_core

Tomcat Java アプリケーションサーバーのインストール、初期化、およびセキュリティベースライン設定を行います。
本 Role は「Core Role」として機能し、アプリケーションごとの JVM 設定や環境変数を注入するための `setenv.sh` 拡張ポイントを提供します。

## Requirements

  * RHEL 8 / 9, AlmaLinux, Rocky Linux
  * Ansible Collection: `community.general`
  * Java (OpenJDK) がインストールされていること（または依存関係として解決されること）

## ⚙️ Role Variables

本 Role で定義されている変数は、以下の2種類に分類されます。

1.  **Defaults (`defaults/main.yml`):** ユーザーがオーバーライド可能な基本設定値。
2.  **Internal Vars (`vars/main.yml`):** OSごとの差異を吸収するための定数（通常は変更不要）。

### 1\. User Configurable Variables (defaults/main.yml)

これらは `group_vars` や Playbook の `vars` で上書きすることを想定したパラメータです。

| 変数名 | デフォルト値 | 説明 |
| :--- | :--- | :--- |
| `tomcat_version` | `"present"` | パッケージの状態（特定のバージョンを指定したい場合はバージョン番号） |
| `tomcat_http_port` | `8080` | デフォルトのHTTPリッスンポート |
| `tomcat_shutdown_port` | `8005` | シャットダウンポート |
| `tomcat_ajp_port` | `8009` | AJPポート |
| `tomcat_user` | `tomcat` | Tomcatプロセスの実行ユーザー |
| `tomcat_group` | `tomcat` | Tomcatプロセスの実行グループ |

**⚠️ 副作用についての注意:**
これらのパラメータを変更した場合、反映のために **Tomcat サービスの再起動（Restart）** が発生します。

### 2\. Internal Constants (vars/main.yml)

これらは Role 内部で OS の差異を吸収するために定義されています。
**原則として変更しないでください。**

| 変数名 | RHEL 8 / 9 設定値 | 説明 |
| :--- | :--- | :--- |
| `tomcat_service_name` | `tomcat` | Systemd サービス名 |
| `tomcat_catalina_home` | `/usr/share/tomcat` | Tomcat インストールディレクトリ |
| `tomcat_conf_dir` | `/etc/tomcat` | 設定ディレクトリ |
| `tomcat_bin_dir` | `/usr/share/tomcat/bin` | バイナリディレクトリ（setenv.sh配置先） |

## 🔧 Extension Mechanism (拡張設定)

本 Role は、JVM オプションや環境変数を **`setenv.sh`** 経由で読み込む設計になっています。
Ansible 変数で複雑な `JAVA_OPTS` を管理しようとせず、スクリプトファイルとして管理することを強く推奨します。

### 設定ファイルの配置ルール

  * **ディレクトリ:** `/usr/share/tomcat/bin/` (またはディストリビューションごとの適切なbinディレクトリ)
  * **ファイル名:** `setenv.sh`
  * **目的:** メモリ設定 (`-Xms`, `-Xmx`)、GC設定、システムプロパティ (`-D...`) の定義

## 📖 Example Playbook

### 基本的な使用法

Core Role を呼び出し、その後にプロジェクト固有の `setenv.sh` を配置します。

```yaml
- hosts: app_servers
  become: true
  
  roles:
    # 1. 基盤設定 (Core Role)
    - role: middleware.middleware.tomcat_core
      vars:
        tomcat_http_port: 8080

  tasks:
    # 2. プロジェクト固有設定 (Project Config)
    # JVM設定などを setenv.sh として配置する
    - name: Deploy Tomcat Environment Config (setenv.sh)
      copy:
        dest: "/usr/share/tomcat/bin/setenv.sh"
        content: |
          #!/bin/sh
          # アプリケーション固有のメモリ設定
          export JAVA_OPTS="-Xms1024m -Xmx2048m -XX:+UseG1GC"
          # その他システムプロパティ
          export JAVA_OPTS="$JAVA_OPTS -Dapp.env=production"
        owner: tomcat
        group: tomcat
        mode: '0755'
      # tomcat_core Role内のハンドラを呼び出して設定を反映させる
      notify: Restart Tomcat
```

## ✅ Quality Assurance (Test Strategy)

本 Role は Molecule により以下の品質が担保されています。

  * **サービス稼働:** Systemd サービスが active であること。
  * **ポート確認:** 指定した HTTP ポート（デフォルト 8080）で Listen していること。
  * **拡張性:** `setenv.sh` に記述した環境変数（JAVA_OPTSなど）がプロセスに反映されていること。
