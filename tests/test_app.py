import importlib.util
import unittest
from unittest.mock import patch

from app import create_app, parse_report, valid_http_url


class ReportParserTests(unittest.TestCase):
    def test_only_installed_apps_with_valid_recorded_endpoints_are_returned(self):
        report = """# Aggregare deployment report

## Applications

### Running App
- Status: Recorded state: running; last recorded check: passed
- Configured endpoint: http://192.168.1.20:8080/ (remote reachability not verified)

### Installed App
- Status: Recorded state: installed; last recorded check: passed
- Endpoint recorded by last application check: https://apps.example.test/home (current reachability not verified)

### Uninstalled App
- Status: Not detected; the application may be disabled, skipped, or not installed
- Configured endpoint: http://192.168.1.20:8090/

### Failed App
- Status: Failed during this installer run; current install state is unverified
- Configured endpoint: http://192.168.1.20:8091/

### Invalid URL App
- Status: Installed service detected; application status is unverified
- Configured endpoint: javascript:alert(1)

### No Endpoint App
- Status: Recorded state: running; last recorded check: passed
- Configured endpoint: unknown or unavailable

## Aggregare-managed systemd services
"""

        self.assertEqual(
            parse_report(report),
            [
                {"name": "Running App", "url": "http://192.168.1.20:8080/"},
                {"name": "Installed App", "url": "https://apps.example.test/home"},
            ],
        )

    def test_health_check_paths_become_app_roots_and_backend_apps_are_hidden(self):
        report = """## Applications

### HabitSync
- Status: Recorded state: running; last recorded check: passed
- Endpoint recorded by last application check: http://192.168.1.20:6842/actuator/health

### Open WebUI
- Status: Recorded state: running; last recorded check: passed
- Configured endpoint: http://192.168.1.20:8080/health

### Vikunja
- Status: Recorded state: running; last recorded check: passed
- Endpoint recorded by last application check: http://192.168.1.20:3456/api/v1/info

### Apmatia
- Status: Recorded state: running; last recorded check: passed
- Endpoint recorded by last application check: http://127.0.0.1:8001/api/version

### Ysparr
- Status: Recorded state: running; last recorded check: passed
- Endpoint recorded by last application check: http://127.0.0.1:8000/health
"""

        self.assertEqual(
            parse_report(report),
            [
                {"name": "HabitSync", "url": "http://192.168.1.20:6842/"},
                {"name": "Open WebUI", "url": "http://192.168.1.20:8080/"},
                {"name": "Vikunja", "url": "http://192.168.1.20:3456/"},
            ],
        )

    def test_malformed_section_does_not_hide_later_valid_app(self):
        report = """## Applications

### Broken [<img src=x onerror=alert(1)>]
- Status: Installed service detected; application status is unverified
- Configured endpoint: http://bad.example.test/

### Good App
- Status: Installed service detected; application status is unverified
- Configured endpoint: http://good.example.test/
"""
        self.assertEqual(parse_report(report)[1], {"name": "Good App", "url": "http://good.example.test/"})

    def test_urls_must_be_http_or_https_without_credentials_or_query_data(self):
        for url in (
            "javascript:alert(1)",
            "http:///missing-host",
            "http://user:password@example.test/",
            "https://example.test/?token=secret",
            "https://example.test/#private",
        ):
            with self.subTest(url=url):
                self.assertFalse(valid_http_url(url))
        self.assertTrue(valid_http_url("https://example.test/apps/"))


@unittest.skipUnless(importlib.util.find_spec("flask"), "Flask dependency is not installed")
class FlaskRouteTests(unittest.TestCase):
    def test_route_renders_links_and_escapes_report_names(self):
        report = """## Applications

### Safe & Sound
- Status: Recorded state: running; last recorded check: passed
- Configured endpoint: http://192.168.1.20:8080/

### <script>alert(1)</script>
- Status: Installed service detected; application status is unverified
- Configured endpoint: http://192.168.1.20:8081/
"""
        app = create_app()
        app.config.update(TESTING=True)

        with patch("app.Path.read_text", return_value=report):
            response = app.test_client().get("/")

        body = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('href="http://192.168.1.20:8080/"', body)
        self.assertIn("Safe &amp; Sound", body)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", body)
        self.assertNotIn("<script>alert(1)</script>", body)

    def test_missing_report_shows_helpful_empty_state(self):
        app = create_app("/path/that/does/not/exist/deployment-report.md")
        app.config.update(TESTING=True)

        response = app.test_client().get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"deployment report is not available yet", response.data)

    def test_report_without_launchable_apps_shows_empty_state(self):
        app = create_app()
        app.config.update(TESTING=True)
        with patch("app.Path.read_text", return_value="## Applications\n\nNo installed applications could be verified.\n"):
            response = app.test_client().get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"No installed applications with a usable web address were found.", response.data)


if __name__ == "__main__":
    unittest.main()
