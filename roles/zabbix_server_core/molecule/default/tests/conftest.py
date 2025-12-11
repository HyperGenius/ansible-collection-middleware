import os
import pytest
import json
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"]
).get_hosts("all")

DUMPED_VARS_FILE = "/tmp/ansible_vars.json"


@pytest.fixture()
def zabbix_vars(host):
    """コンテナ内にダンプされたAnsible変数を読み込むフィクスチャ"""
    vars_file = host.file(DUMPED_VARS_FILE)

    if not vars_file.exists:
        pytest.skip("ダンプされた変数ファイルが見つかりません")

    try:
        vars_json = json.loads(vars_file.content_string)
        return vars_json
    except json.JSONDecodeError:
        pytest.fail("ダンプされた変数ファイルの内容がJSON形式ではありません")
