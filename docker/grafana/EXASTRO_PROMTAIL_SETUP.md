# Promtail によるログ転送セットアップ

## 概要

`promtail` コンテナを追加することで、Exastro の全コンテナログおよび監査ログを
別サーバの **Grafana + Loki** へ自動転送できます。

```
[Exastro サーバ]                        [監視サーバ]
  promtail コンテナ  ──HTTP push──►  Loki  ◄──  Grafana
      │
      ├─ Docker 全コンテナの stdout/stderr
      └─ /var/log/exastro/*.log（監査ログ）
```

収集するログの種別:

| ジョブ名 | 収集対象 | 主なラベル |
| --- | --- | --- |
| `docker` | 全コンテナの stdout/stderr | `container`, `compose_service`, `stream` |
| `exastro-audit` | `/var/log/exastro/*.log` | `job=exastro-audit` |


## 前提条件

- Docker Compose v2.x 以上（または docker-compose v1.29 以上）
- 別サーバに Loki が起動済みであること
- Loki の Bearer Token を取得済みであること（認証なしの場合は空文字を設定）
- Docker ソケット `/var/run/docker.sock` が読み取り可能であること


## 設定手順

### 1. `.env` に Loki 接続先を設定

`.env` の以下の項目を編集します。

```shell
### Promtail / Loki log forwarding
LOKI_URL=http://<loki-server-ip>:3100
# PROMTAIL_VERSION=3.0.0   # バージョンを固定したい場合はコメントを外す
```

**設定例（`http://192.168.10.13:13100` に転送する場合）:**

```
LOKI_URL=http://192.168.10.13:13100
```

### 2. `promtail/exastro-config.yml` の確認・カスタマイズ（任意）

デフォルトの [promtail/exastro-config.yml](promtail/config.yml) はそのまま利用できます。
収集ジョブや pipeline_stages を追加したい場合のみ編集してください。

```yaml
clients:
  - url: ${LOKI_URL}/loki/api/v1/push
```

設定ファイル内の `${変数名}` は起動時に `.env` の値で自動展開されます（`--config.expand-env=true` オプションによる）。


### 3. `docker-compose.yml` に `promtail` サービスを追加
exastro の `docker-compose.yml` に以下の `promtail` サービス定義を追加します。

```yaml
  promtail:
    image: docker.io/grafana/promtail:${PROMTAIL_VERSION:-3.0.0}
    container_name: promtail
    hostname: promtail
    restart: always
    command: -config.file=/etc/promtail/exastro-config.yml -config.expand-env=true
    environment:
      LOKI_URL: ${LOKI_URL}
    volumes:
      - ./promtail/exastro-config.yml:/etc/promtail/exastro-config.yml:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - vol-exastro-log:/var/log/exastro:ro
    networks:
      - exastro
    profiles:
      - all
      - monitoring
    logging: *logging
```

## 起動方法

### Promtail のみを追加起動する（既存コンテナはそのまま）

既に Exastro が動作している環境に promtail だけ追加する場合:

```shell
# Docker 環境
docker compose --profile monitoring up -d promtail

# Podman 環境
docker-compose --profile monitoring up -d promtail
```

### COMPOSE_PROFILES に追加して常時有効化する

`.env` の `COMPOSE_PROFILES` に `monitoring` を追加することで、
`docker compose up` 実行時に promtail も常に起動対象になります。

```
# .env
COMPOSE_PROFILES=base,monitoring
```

その後:

```shell
docker compose up -d --wait
```

### `all` プロファイルで全コンテナと一緒に起動

`all` プロファイルには `monitoring` が含まれています。

```shell
docker compose --profile all up -d --wait
```


## 動作確認

### コンテナの起動確認

```shell
docker compose ps promtail
```

```
NAME        IMAGE                       STATUS         PORTS
promtail    grafana/promtail:3.0.0      Up 2 minutes
```

### ログ確認（エラーがないこと）

```shell
docker compose logs promtail -f
```

正常時の出力例:

```
level=info ts=... caller=main.go msg="Starting Promtail" version=...
level=info ts=... caller=server.go msg="server listening on addresses" http=0.0.0.0:9080
level=info ts=... caller=docker.go msg="added target" container=exastro ...
```

### Promtail の Ready エンドポイント確認

```shell
curl -s http://localhost:9080/ready
```

`ready` と返れば正常です。

### 検出されているターゲット一覧

```shell
curl -s http://localhost:9080/api/v1/targets | python3 -m json.tool | grep -E '"job"|"container"|"health"'
```

### Grafana で確認

Grafana の Explore 画面で Loki を選択し、下記のようなクエリでログが届いているか確認します。

```logql
# 全コンテナのログ
{compose_project="exastro"}

# 特定コンテナのログ
{container="platform-auth"}

# 監査ログのみ
{job="exastro-audit"}
```


## 収集されるラベル一覧

Loki に付与されるラベルの一覧です。

| ラベル名 | 値の例 | 説明 |
| --- | --- | --- |
| `container` | `platform-auth` | コンテナ名 |
| `compose_service` | `platform-auth` | Docker Compose サービス名 |
| `compose_project` | `exastro` | Docker Compose プロジェクト名 |
| `stream` | `stdout` / `stderr` | 出力ストリーム |
| `job` | `docker` / `exastro-audit` | 収集ジョブ名 |


## 停止方法

```shell
docker compose stop promtail
docker compose rm -f promtail
```


## トラブルシューティング

### ログに `connection refused` が表示される

Loki サーバに疎通できていません。
`.env` の `LOKI_URL` が正しいか、またファイアウォールでポートが開いているか確認してください。

```shell
# 疎通確認
curl -v ${LOKI_URL}/ready
```

### コンテナログが Loki に届かない

`/var/lib/docker/containers` のマウントが正しいか確認してください。
ホストの Docker ルートディレクトリが `/var/lib/docker` 以外の場合は
[promtail/config.yml](promtail/config.yml) の `docker_sd_configs` の設定と
`docker-compose.yml` のボリュームマウントパスを変更してください。

```shell
# Docker のルートディレクトリを確認
docker info | grep "Docker Root Dir"
```

### 監査ログが届かない

`platform-auth` の `AUDIT_LOG_ENABLED=True` が設定されているか、
および `vol-exastro-log` ボリュームにファイルが生成されているか確認してください。

```shell
ls -la .volumes/exastro/log/
```


## パラメータ一覧

`.env` で設定可能な Promtail 関連のパラメータです。

| パラメータ名 | デフォルト値 | 説明 |
| --- | --- | --- |
| `LOKI_URL` | （必須） | Loki の Push エンドポイント（例: `http://192.168.10.13:3100`） |
| `PROMTAIL_VERSION` | `3.0.0` | 使用する Promtail イメージのバージョン |
