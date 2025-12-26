"""
Pytest conftest for Zabbix Agent 2 tests
"""
import json
import pytest


@pytest.fixture()
def zabbix_vars(host):
    """Load Zabbix Agent variables from JSON file"""
    vars_file = host.file("/tmp/test_data/zabbix_agent_vars.json")
    if not vars_file.exists:
        pytest.skip("Variable dump file not found")
    
    content = vars_file.content_string
    return json.loads(content)
