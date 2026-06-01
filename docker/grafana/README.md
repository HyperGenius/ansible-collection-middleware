# Grafana 監視スタック

Grafana + Loki + Promtail によるログ監視環境を Docker Compose で構築します。
Zabbix はデータソースとして外部連携します。

## 構成

| コンテナ | イメージ | ホストポート | 役割 |
|---|---|---|---|
| grafana | grafana/grafana:latest | 13000 | 可視化・ダッシュボード |
| loki | grafana/loki:latest | 13100 | ログ集約バックエンド |
| promtail | grafana/promtail:latest | 9080 | ローカルログ収集エージェント |

```
【Grafanaサーバー】
Zabbix (外部)  ──┐
                  ├──► Grafana (:13000)
Loki (:13100) ◄──┘
  ▲  ▲
  │  └─── Promtail (ローカル) ◄── /var/log/*log
  │
  └─────── Promtail (リモート) ◄── Docker コンテナログ
              【別サーバー】
```

## ディレクトリ構成

```
docker/grafana/
├── docker-compose.yaml               # Grafana + Loki + Promtail (ローカル用)
├── grafana/
│   └── provisioning/
│       └── datasources/
│           └── datasources.yaml      # データソース自動設定
├── loki/
│   └── loki-config.yaml
└── promtail/
    ├── promtail-config.yaml          # ローカルサーバー用設定
    ├── promtail-docker-config.yaml   # リモートサーバー用 Docker コンテナ監視設定
    └── docker-compose.remote.yaml    # リモートサーバーにデプロイする Compose ファイル
```

## セットアップ

### 1. Zabbix 接続先の設定

`grafana/provisioning/datasources/datasources.yaml` を編集します。

```yaml
- name: Zabbix
  url: http://<zabbix-webサーバーのホスト>/api_jsonrpc.php
  jsonData:
    username: <Zabbixユーザー名>
  secureJsonData:
    password: <Zabbixパスワード>
```

### 2. 起動

```bash
docker compose up -d
```

### 3. Grafana へのアクセス

- URL: http://localhost:3000
- 初期ユーザー: `admin`
- 初期パスワード: `admin`（初回ログイン時に変更を求められます）

### 4. Zabbix プラグインの有効化

1. Grafana にログイン
2. `Administration` → `Plugins` → `Zabbix` を検索
3. `Enable` をクリック

## データ永続化

以下のボリュームで永続化されます。

| ボリューム | マウント先 | 内容 |
|---|---|---|
| grafana_data | /var/lib/grafana | ダッシュボード・設定・SQLite DB |
| loki_data | /loki | 収集済みログデータ |

## ログ収集の設定変更

デフォルトでは `/var/log/*log` を収集します。
対象を変更する場合は `promtail/promtail-config.yaml` の `__path__` を編集してください。

```yaml
labels:
  __path__: /var/log/*log   # ← 収集対象のパス
```

## リモートサーバーの Docker コンテナ監視

別サーバーで動作しているコンテナアプリのログを収集する場合、そのサーバーに Promtail のみをデプロイします。

### 1. ファイルをリモートサーバーへ転送

```bash
scp promtail/docker-compose.remote.yaml  <user>@<remote-host>:~/promtail/docker-compose.yaml
scp promtail/promtail-docker-config.yaml <user>@<remote-host>:~/promtail/promtail-docker-config.yaml
```

### 2. Loki の接続先を設定

リモートサーバー上の `promtail-docker-config.yaml` を編集し、GrafanaサーバーのIPを指定します。

```yaml
clients:
  - url: http://<GRAFANA_SERVER_IP>:13100/loki/api/v1/push
```

### 3. リモートサーバーで起動

```bash
cd ~/promtail
docker compose up -d
```

### 収集されるラベル

| ラベル | 内容 |
|---|---|
| `container` | コンテナ名 |
| `image` | イメージ名 |
| `stream` | stdout / stderr |
| `host` | リモートサーバーのホスト名 |

### ネットワーク要件

リモートサーバーから Grafana サーバーの **13100 番ポート** への通信を許可してください。

```
リモートサーバー → GrafanaサーバーIP:13100 (TCP)
```

## 停止・削除

```bash
# 停止
docker compose down

# ボリュームごと削除（データも消えます）
docker compose down -v
```

## 注意事項

- `GF_SECURITY_ADMIN_PASSWORD` は本番環境では環境変数や `.env` ファイルで管理してください
- Promtail が `/var/log` を読むため、ホスト側のパーミッションに注意してください
- Loki のログ保持期間はデフォルト 30 日です（`loki/loki-config.yaml` の `retention_period` で変更可）
