def test_tomcat_port(host, tomcat_vars):
    """ポート 8080 でリッスンしていること (TCP)"""
    tomcat_http_port = tomcat_vars["tomcat_http_port"]
    socket = host.socket(f"tcp://{tomcat_http_port}")
    assert socket.is_listening
