def test_tomcat_service(host, tomcat_vars):
    """Systemdサービス (tomcat) が起動していること (is_running)"""
    service_name = tomcat_vars["tomcat_service_name"]
    service = host.service(service_name)
    assert service.is_running

    # Systemdサービス (tomcat) が自動起動設定になっていること
    assert service.is_enabled
