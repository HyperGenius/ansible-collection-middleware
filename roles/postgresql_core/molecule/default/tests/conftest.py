# roles/postgresql_core/molecule/default/tests/conftest.py
import os
import json
import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ.get("MOLECULE_INVENTORY_FILE")
).get_hosts("all")


@pytest.fixture(scope="module")
def postgresql_vars(host):
    """コンテナ内にダンプされたAnsible変数を読み込むフィクスチャ"""

    vars_file = host.file("/tmp/ansible_vars.json")
    assert vars_file.exists
    assert vars_file.is_file
    assert vars_file.mode == 0o644
    assert vars_file.user == "root"
    assert vars_file.group == "root"

    return json.loads(vars_file.content_string)
