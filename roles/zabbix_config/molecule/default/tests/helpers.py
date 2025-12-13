import requests


def post_zabbix_api(
    zabbix_config_vars: dict, payload: dict, timeout: int = 30
) -> requests.Response:
    """
    Zabbix APIリクエストを送信する
    """
    api_url = zabbix_config_vars["zabbix_api_url"]
    auth_token = zabbix_config_vars["zabbix_auth_token"]

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + auth_token,
    }

    response = requests.post(api_url, json=payload, headers=headers, timeout=timeout)

    return response
