# GitLab Backup ロール

オンプレミス GitLab のバックアップを取得し、rsync または S3 互換ストレージへ転送するロール。

## 概要

このロールは以下を行います:

- `gitlab-backup create` によるデータバックアップの取得
- `gitlab.rb` / `gitlab-secrets.json` の設定ファイルアーカイブ
- バックアップファイルをリモートへ転送（rsync または S3 互換ストレージ）
- 指定した世代数を超えた古いバックアップの自動削除
- バックアップ結果のログ出力（JSON ステータスファイル + テキストログ）

## サポートされるプラットフォーム

- RHEL 8, 9 / AlmaLinux 8, 9 / Rocky Linux 8, 9
- Ubuntu 20.04 (Focal), 22.04 (Jammy)

## 前提条件

### GitLab ホスト側

| 条件 | rsync | S3 |
|---|:---:|:---:|
| `gitlab-backup` コマンドが利用可能 (GitLab インストール済み) | ✓ | ✓ |
| `rsync` コマンドがインストール済み | ✓ | - |
| `aws` CLI がインストール済み | - | ✓ |
| バックアップサーバーへの SSH 疎通 | ✓ | - |
| S3 エンドポイントへのネットワーク疎通 | - | ✓ |

### rsync 転送を使用する場合

**SSH 鍵の事前配置が必要です。**

1. バックアップ専用の SSH キーペアを生成する:
   ```bash
   ssh-keygen -t ed25519 -f /var/opt/gitlab/.ssh/backup_id_ed25519 -N "" -C "gitlab-backup"
   chown git:git /var/opt/gitlab/.ssh/backup_id_ed25519*
   chmod 600 /var/opt/gitlab/.ssh/backup_id_ed25519
   ```

2. 公開鍵をバックアップサーバーの対象ユーザーの `~/.ssh/authorized_keys` に登録する:
   ```bash
   # バックアップサーバー上で実行
   cat >> ~/.ssh/authorized_keys << 'EOF'
   <GitLabホストの backup_id_ed25519.pub の内容>
   EOF
   ```

3. ロール変数に鍵のパスを指定する:
   ```yaml
   gitlab_backup_rsync_ssh_private_key_path: /var/opt/gitlab/.ssh/backup_id_ed25519
   ```

> **注意**: Ansible がGitLabホストへの接続に使う鍵と、バックアップサーバーへの rsync 用鍵は別の鍵を使用してください。用途を分離することでセキュリティリスクを低減します。

### S3 転送を使用する場合 (MinIO 等のオンプレミス S3 互換ストレージを含む)

**AWS CLI の認証情報の事前設定が必要です。**

- AWS S3 の場合: IAM ロール、`~/.aws/credentials`、または環境変数 (`AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`) のいずれかで認証を設定してください。
- オンプレミス S3 互換ストレージ (MinIO 等) の場合: `~/.aws/credentials` にアクセスキーを設定し、`gitlab_backup_s3_endpoint_url` にエンドポイント URL を指定してください。

`become: true` で実行されるため、認証情報は `root` ユーザーのホームディレクトリ (`/root/.aws/`) に配置してください。

### インベントリグループ

このロールは以下のグループ名を参照します（変数で変更可能）:

| 変数 | デフォルト | 用途 |
|---|---|---|
| `gitlab_backup_gitlab_group` | `gitlab` | ロールを適用するGitLabホストのグループ |
| `gitlab_backup_backup_group` | `backup` | rsync の古い世代削除で `delegate_to` するバックアップサーバーのグループ |

インベントリ例:
```ini
[gitlab]
gitlab01.example.com

[backup]
backup01.example.com
```

## ロール変数

### バックアップ基本設定

| 変数 | デフォルト | 説明 |
|---|---|---|
| `gitlab_backup_path` | `/var/opt/gitlab/backups` | GitLab バックアップファイルの保存先 |
| `gitlab_backup_status_file` | `/var/log/gitlab/backup_status.json` | バックアップステータスの JSON 出力先 |
| `gitlab_backup_log_file` | `/var/log/gitlab/backup.log` | バックアップログの出力先 |
| `gitlab_backup_transfer_method` | `rsync` | 転送方式: `rsync` または `s3` |
| `gitlab_backup_generations` | `7` | 保持する世代数。`0` で無制限。 |

### rsync 設定

| 変数 | デフォルト | 説明 |
|---|---|---|
| `gitlab_backup_rsync_host` | `""` | バックアップサーバーのホスト名または IP |
| `gitlab_backup_rsync_user` | `git` | バックアップサーバーへの SSH ユーザー |
| `gitlab_backup_rsync_dest_path` | `""` | バックアップサーバー上の転送先パス |
| `gitlab_backup_rsync_ssh_private_key_path` | `""` | GitLab ホスト上の SSH 秘密鍵パス。未指定でrsyncのデフォルト鍵を使用。 |
| `gitlab_backup_rsync_remove_source` | `false` | 転送成功後にGitLabホスト上のバックアップを削除するか。デフォルト `false` (安全側)。 |

### S3 設定

| 変数 | デフォルト | 説明 |
|---|---|---|
| `gitlab_backup_s3_bucket` | `""` | S3 バケット名 |
| `gitlab_backup_s3_prefix` | `"gitlab-backups/"` | バケット内のプレフィックス (末尾スラッシュ必須) |
| `gitlab_backup_s3_region` | `""` | AWS リージョン。未指定でデフォルトを使用。 |
| `gitlab_backup_s3_endpoint_url` | `""` | オンプレミス S3 互換ストレージの URL。AWS S3 の場合は空文字。 |
| `gitlab_backup_s3_profile` | `""` | AWS CLI プロファイル名。未指定でデフォルトプロファイルを使用。 |

### インベントリグループ名設定

| 変数 | デフォルト | 説明 |
|---|---|---|
| `gitlab_backup_gitlab_group` | `gitlab` | GitLab ホストのインベントリグループ名 |
| `gitlab_backup_backup_group` | `backup` | バックアップサーバーのインベントリグループ名 (rsync のみ使用) |

## バックアップサーバーを Ansible 実行サーバー自身とする際の注意点

rsync 転送先として Ansible 実行サーバー（いわゆる localhost）を指定したい場合、以下の点に注意が必要です。

### `localhost` は GitLab ホスト自身を指す

`transfer_rsync.yml` の rsync コマンドは **GitLab ホスト上で実行**されます。そのため、`gitlab_backup_rsync_host: localhost` と指定すると、GitLab ホスト自身の loopback アドレスへ接続しようとし、意図した動作になりません。

```
# 誤り: GitLab ホスト自身に SSH 接続しようとする
gitlab_backup_rsync_host: localhost

# 正しい: GitLab ホストから見た Ansible 実行サーバーの実際の IP を指定する
gitlab_backup_rsync_host: 192.168.1.10
```

### 古い世代の削除タスクにも設定が必要

古い世代の削除タスクは `delegate_to: groups[gitlab_backup_backup_group][0]` でバックアップサーバーに接続します。バックアップ先が Ansible 実行サーバーの場合、インベントリに `localhost` を追加し `ansible_connection: local` を設定してください。

```ini
# inventory
[gitlab]
gitlab01.example.com

[backup]
localhost ansible_connection=local
```

### プレイブック例

```yaml
- hosts: gitlab
  become: true
  roles:
    - role: middleware.middleware.gitlab_backup
      vars:
        gitlab_backup_transfer_method: rsync
        gitlab_backup_rsync_host: 192.168.1.10        # Ansible実行サーバーの実際のIP
        gitlab_backup_rsync_user: ansible
        gitlab_backup_rsync_dest_path: /mnt/backups/gitlab
        gitlab_backup_rsync_ssh_private_key_path: /var/opt/gitlab/.ssh/backup_id_ed25519
        gitlab_backup_backup_group: backup             # インベントリの [backup] グループを参照
```

## 依存関係

なし。

## プレイブックの例

### rsync で転送する場合

```yaml
- hosts: gitlab
  become: true
  roles:
    - role: middleware.middleware.gitlab_backup
      vars:
        gitlab_backup_transfer_method: rsync
        gitlab_backup_rsync_host: backup01.example.com
        gitlab_backup_rsync_user: git
        gitlab_backup_rsync_dest_path: /mnt/backups/gitlab
        gitlab_backup_rsync_ssh_private_key_path: /var/opt/gitlab/.ssh/backup_id_ed25519
        gitlab_backup_generations: 14
```

### MinIO (オンプレミス S3 互換) で転送する場合

```yaml
- hosts: gitlab
  become: true
  roles:
    - role: middleware.middleware.gitlab_backup
      vars:
        gitlab_backup_transfer_method: s3
        gitlab_backup_s3_bucket: gitlab-backups
        gitlab_backup_s3_prefix: "production/"
        gitlab_backup_s3_endpoint_url: https://minio.example.com
        gitlab_backup_generations: 30
```

### AWS S3 で転送する場合

```yaml
- hosts: gitlab
  become: true
  roles:
    - role: middleware.middleware.gitlab_backup
      vars:
        gitlab_backup_transfer_method: s3
        gitlab_backup_s3_bucket: my-company-gitlab-backups
        gitlab_backup_s3_prefix: "gitlab/"
        gitlab_backup_s3_region: ap-northeast-1
        gitlab_backup_generations: 30
```

## ログ出力

バックアップ結果は以下の2ファイルに記録されます:

**`/var/log/gitlab/backup_status.json`** — 最新のバックアップステータス (上書き):
```json
{
  "timestamp": "2026-06-01T03:00:00Z",
  "status": "success",
  "rc": 0,
  "transfer_method": "rsync"
}
```

**`/var/log/gitlab/backup.log`** — 実行履歴の追記ログ:
```
2026-06-01T03:00:00Z [SUCCESS] GitLab backup completed. transfer=rsync rc=0
2026-05-31T03:00:00Z [SUCCESS] GitLab backup completed. transfer=rsync rc=0
```

## ライセンス

MIT

## 著者情報

HyperGenius
