# roles/postgresql_core/molecule/default/tests/conftest.py
import os
import pytest
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ.get("MOLECULE_INVENTORY_FILE")
).get_hosts("all")
