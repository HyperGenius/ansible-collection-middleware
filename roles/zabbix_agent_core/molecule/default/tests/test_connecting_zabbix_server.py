import requests
import json
from .conftest import get_zabbix_auth_token


def test_zabbix_server_reachability(host):
    """AgentからZabbix Server (10051) への疎通確認"""
    # Zabbix Serverのコンテナ名（またはIP）を指定
    zabbix_server = "zabbix-server"

    # ncコマンド等でポート確認 (コンテナにncが必要)
    # または /dev/tcp を使うハック
    cmd = host.run(f"bash -c 'cat < /dev/null > /dev/tcp/{zabbix_server}/10051'")
    assert cmd.rc == 0


def test_agent_registered_in_server(host):
    """Zabbix Server上にAgentホストが自動登録されているか確認"""

    # moleculeテストサーバからZabbix Serverへアクセス
    zabbix_server_hostname = "127.0.0.1"
    zabbix_server_port = "8080"

    # Zabbix Serverのコンテナ名（またはIP）を指定
    zabbix_url = f"http://{zabbix_server_hostname}:{zabbix_server_port}/api_jsonrpc.php"

    # 認証トークン取得
    auth_token = get_zabbix_auth_token(zabbix_server_hostname, zabbix_server_port)

    # Agentのホスト名 (インベントリ等から取得するのが理想)
    agent_hostname = "zabbix-agent-rhel"

    # APIでホスト検索
    payload = {
        "jsonrpc": "2.0",
        "method": "host.get",
        "params": {"filter": {"host": [agent_hostname]}, "output": "extend"},
        "id": 1,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + auth_token,
    }
    response = requests.post(zabbix_url, data=json.dumps(payload), headers=headers)
    result = response.json()["result"]

    # 検証
    assert len(result) == 1
    assert result[0]["host"] == agent_hostname
