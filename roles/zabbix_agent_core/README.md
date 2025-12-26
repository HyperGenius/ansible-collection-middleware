# Zabbix Agent Core Role

Cross-platform Zabbix Agent 2 installation and configuration role for Linux (RHEL-based) and Windows Server.

## Overview

This role installs and configures Zabbix Agent 2 (Go-based agent) on both Linux and Windows systems. It provides baseline configuration for:
- Installation from official Zabbix repositories
- Auto-registration with Zabbix Server
- Extensible configuration via `conf.d` pattern (Linux)
- Firewall configuration

## Supported Platforms

### Linux
- RHEL 8, 9
- AlmaLinux 8, 9
- Rocky Linux 8, 9

### Windows
- Windows Server 2019
- Windows Server 2022
- Windows Server 2025

## Requirements

### Linux
- Ansible 2.9 or higher
- `ansible.posix` collection (for firewalld module)

### Windows
- Ansible 2.9 or higher
- `ansible.windows` collection
- `community.windows` collection

Install required collections:
```bash
ansible-galaxy collection install ansible.posix ansible.windows community.windows
```

## Role Variables

### Core Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `zabbix_agent_core_version` | `"7.0"` | Zabbix major version to install |
| `zabbix_agent_core_server` | `"127.0.0.1"` | Zabbix Server IP for passive checks |
| `zabbix_agent_core_server_active` | `"127.0.0.1"` | Zabbix Server IP for active checks |
| `zabbix_agent_core_hostname` | `{{ inventory_hostname }}` | Hostname as it appears in Zabbix |
| `zabbix_agent_core_host_metadata` | `"Linux"` or `"Windows"` | Host metadata for auto-registration |
| `zabbix_agent_core_listen_port` | `10050` | Listen port for passive checks |

### Linux-Specific Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `zabbix_agent_core_config_file_linux` | `/etc/zabbix/zabbix_agent2.conf` | Configuration file path |
| `zabbix_agent_core_include_dir` | `/etc/zabbix/zabbix_agent2.d` | Directory for additional configs |
| `zabbix_agent_core_log_file_linux` | `/var/log/zabbix/zabbix_agent2.log` | Log file path |
| `zabbix_agent_core_service_name_linux` | `zabbix-agent2` | Service name |

### Windows-Specific Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `zabbix_agent_core_windows_version` | `"7.0.6"` | Exact Windows installer version |
| `zabbix_agent_core_config_file_windows` | `C:\Program Files\Zabbix Agent 2\zabbix_agent2.conf` | Configuration file path |
| `zabbix_agent_core_log_file_windows` | `C:\Program Files\Zabbix Agent 2\zabbix_agent2.log` | Log file path |
| `zabbix_agent_core_service_name_windows` | `Zabbix Agent 2` | Service name |

### Other Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `zabbix_agent_core_configure_firewall` | `true` | Whether to configure firewall rules |
| `zabbix_agent_core_service_state` | `started` | Desired service state |
| `zabbix_agent_core_service_enabled` | `true` | Enable service at boot |

## Dependencies

None.

## Example Playbook

### Basic Usage (Linux)

```yaml
- hosts: linux_servers
  become: true
  roles:
    - role: middleware.middleware.zabbix_agent_core
      vars:
        zabbix_agent_core_server: "192.168.1.100"
        zabbix_agent_core_server_active: "192.168.1.100"
        zabbix_agent_core_hostname: "{{ inventory_hostname }}"
```

### Basic Usage (Windows)

```yaml
- hosts: windows_servers
  roles:
    - role: middleware.middleware.zabbix_agent_core
      vars:
        zabbix_agent_core_server: "192.168.1.100"
        zabbix_agent_core_server_active: "192.168.1.100"
        zabbix_agent_core_hostname: "{{ inventory_hostname }}"
```

### Advanced Configuration (Linux with Custom Parameters)

```yaml
- hosts: linux_servers
  become: true
  roles:
    - role: middleware.middleware.zabbix_agent_core
      vars:
        zabbix_agent_core_server: "192.168.1.100"
        zabbix_agent_core_server_active: "192.168.1.100"
        zabbix_agent_core_host_metadata: "Linux DB Production"

  tasks:
    # Add custom UserParameter after agent installation
    - name: Deploy custom monitoring parameters
      ansible.builtin.copy:
        dest: /etc/zabbix/zabbix_agent2.d/custom-monitoring.conf
        content: |
          # Custom monitoring parameters
          UserParameter=custom.check,/usr/local/bin/custom_check.sh
        owner: zabbix
        group: zabbix
        mode: '0640'
      notify: Restart Zabbix Agent 2
```

## Extensibility

### Linux: conf.d Pattern

The role creates an include directory (`/etc/zabbix/zabbix_agent2.d/`) for additional configuration files. You can deploy custom `UserParameter` definitions, TLS settings, or other configurations by placing `.conf` files in this directory.

Example project-specific role:

```yaml
# roles/my_app_monitoring/tasks/main.yml
- name: Deploy application-specific monitoring
  ansible.builtin.template:
    src: app-monitoring.conf.j2
    dest: /etc/zabbix/zabbix_agent2.d/99-app-monitoring.conf
    owner: zabbix
    group: zabbix
    mode: '0640'
  notify: Restart Zabbix Agent 2
```

## Handlers

The role provides the following handlers:

- `Restart Zabbix Agent 2` - Restarts the Zabbix Agent 2 service (Linux)
- `Restart Zabbix Agent 2 (Windows)` - Restarts the Zabbix Agent 2 service (Windows)

## Testing

### Molecule (Linux)

The role includes Molecule tests for Linux platforms:

```bash
cd roles/zabbix_agent_core
molecule test
```

To test with different distributions:

```bash
MOLECULE_DISTRO=rockylinux9 molecule test
MOLECULE_DISTRO=rockylinux8 molecule test
```

## License

MIT

## Author Information

HyperGenius
