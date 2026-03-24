"""Tests for web server domain discovery."""

from cloud_map.models import WebServerType
from cloud_map.webserver import _parse_httpd_line, _parse_nginx_line


class TestParseNginxLine:
    def test_single_domain(self):
        line = "/etc/nginx/sites-enabled/app.conf:3:    server_name example.com;"
        result = _parse_nginx_line(line)
        assert len(result) == 1
        assert result[0].domain == "example.com"
        assert result[0].web_server_type == WebServerType.NGINX
        assert result[0].config_file == "/etc/nginx/sites-enabled/app.conf"

    def test_multiple_domains(self):
        line = "/etc/nginx/conf.d/site.conf:5:    server_name example.com www.example.com;"
        result = _parse_nginx_line(line)
        assert len(result) == 2
        assert result[0].domain == "example.com"
        assert result[1].domain == "www.example.com"

    def test_underscore_ignored(self):
        line = "/etc/nginx/sites-enabled/default:1:    server_name _;"
        result = _parse_nginx_line(line)
        assert len(result) == 0

    def test_localhost_ignored(self):
        line = "/etc/nginx/conf.d/local.conf:2:    server_name localhost;"
        result = _parse_nginx_line(line)
        assert len(result) == 0

    def test_mixed_ignored_and_real(self):
        line = "/etc/nginx/conf.d/site.conf:3:    server_name _ example.com localhost;"
        result = _parse_nginx_line(line)
        assert len(result) == 1
        assert result[0].domain == "example.com"

    def test_no_match(self):
        line = "/etc/nginx/nginx.conf:10:    # server_name not a real directive"
        result = _parse_nginx_line(line)
        assert len(result) == 0

    def test_empty_line(self):
        result = _parse_nginx_line("")
        assert len(result) == 0


class TestParseHttpdLine:
    def test_server_name(self):
        line = "/etc/apache2/sites-enabled/app.conf:5:    ServerName example.com"
        result = _parse_httpd_line(line)
        assert len(result) == 1
        assert result[0].domain == "example.com"
        assert result[0].web_server_type == WebServerType.HTTPD
        assert result[0].config_file == "/etc/apache2/sites-enabled/app.conf"

    def test_server_alias_multiple(self):
        line = "/etc/httpd/conf.d/vhost.conf:8:    ServerAlias www.example.com api.example.com"
        result = _parse_httpd_line(line)
        assert len(result) == 2
        assert result[0].domain == "www.example.com"
        assert result[1].domain == "api.example.com"

    def test_case_insensitive(self):
        line = "/etc/apache2/sites-enabled/app.conf:5:    servername Example.Com"
        result = _parse_httpd_line(line)
        assert len(result) == 1
        assert result[0].domain == "Example.Com"

    def test_no_match(self):
        line = "/etc/apache2/apache2.conf:1:    # ServerName is commented"
        result = _parse_httpd_line(line)
        assert len(result) == 0

    def test_empty_line(self):
        result = _parse_httpd_line("")
        assert len(result) == 0

    def test_localhost_ignored(self):
        line = "/etc/httpd/conf/httpd.conf:3:    ServerName localhost"
        result = _parse_httpd_line(line)
        assert len(result) == 0
