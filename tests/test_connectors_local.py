import io
import os
import pathlib
import sys
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "connectors"))

import onpage  # noqa: E402
import linkgraph  # noqa: E402
import schema_lint  # noqa: E402
import robots  # noqa: E402
import psi  # noqa: E402
import ledger  # noqa: E402
import openpagerank  # noqa: E402
import resend  # noqa: E402
import firecrawl  # noqa: E402
import robots as robots_mod  # noqa: E402
import tavily  # noqa: E402
import doh  # noqa: E402
import pageviews  # noqa: E402
import gdelt  # noqa: E402
import youtube  # noqa: E402
import indexpush  # noqa: E402
import hn  # noqa: E402
import producthunt  # noqa: E402
import xquik  # noqa: E402
import appstore  # noqa: E402
import bluesky  # noqa: E402
import fediverse  # noqa: E402
import discourse  # noqa: E402
import experiment  # noqa: E402
import sitemap  # noqa: E402
import kg  # noqa: E402
import crawl  # noqa: E402
import rss_monitor  # noqa: E402
import suggest  # noqa: E402
import wayback  # noqa: E402
import _http  # noqa: E402
import _loader  # noqa: E402
import datetime as _dt  # noqa: E402


class SharedHttpSafetyTests(unittest.TestCase):
    def test_non_public_destinations_are_blocked_by_default(self):
        for url in (
            "http://127.0.0.1/admin",
            "http://[::1]/",
            "http://169.254.169.254/latest/meta-data/",
            "http://10.0.0.1/",
        ):
            with self.subTest(url=url):
                self.assertIn("non-public", _http.url_safety_error(url))

    def test_multicast_reserved_nat64_and_embedded_private_are_blocked(self):
        addresses = (
            "224.0.0.1",              # multicast can report is_global=True
            "ff0e::1",                # globally scoped IPv6 multicast
            "240.0.0.1",              # reserved IPv4
            "64:ff9b::5db8:d822",      # NAT64, even with a public embedded IPv4
            "::ffff:127.0.0.1",        # IPv4-mapped loopback
            "2002:7f00:1::",           # 6to4 with embedded loopback
        )
        for address in addresses:
            family = _http.socket.AF_INET6 if ":" in address else _http.socket.AF_INET
            answer = [(family, _http.socket.SOCK_STREAM, 6, "", (address, 443))]
            with self.subTest(address=address), \
                 mock.patch.object(_http.socket, "getaddrinfo", return_value=answer):
                self.assertIn("non-public", _http.url_safety_error("https://blocked.test/"))
                self.assertIn(
                    "non-public",
                    _http.url_safety_error("https://blocked.test/", allow_private=True),
                )

    def test_private_access_requires_explicit_opt_in(self):
        self.assertIsNone(_http.url_safety_error("http://127.0.0.1/", allow_private=True))

    def test_non_http_and_embedded_credentials_are_blocked(self):
        self.assertIn("scheme", _http.url_safety_error("ftp://example.com/file"))
        self.assertIn("credentials", _http.url_safety_error("https://user:placeholder@example.com/"))
        self.assertIn("port", _http.url_safety_error("https://example.com:not-a-port/"))

    def test_all_resolved_addresses_must_be_public(self):
        answers = [
            (2, 1, 6, "", ("93.184.216.34", 443)),
            (2, 1, 6, "", ("127.0.0.1", 443)),
        ]
        with mock.patch.object(_http.socket, "getaddrinfo", return_value=answers):
            self.assertIn("127.0.0.1", _http.url_safety_error("https://mixed.test/"))

    def test_redirect_handler_revalidates_target(self):
        handler = _http._ValidatedRedirectHandler()
        req = _http.urllib.request.Request("https://example.com/")
        with self.assertRaises(_http.BlockedURL):
            handler.redirect_request(req, None, 302, "Found", {}, "http://127.0.0.1/")

    def test_redirect_blocks_tls_downgrade(self):
        public = [(2, 1, 6, "", ("93.184.216.34", 80))]
        handler = _http._ValidatedRedirectHandler()
        req = _http.urllib.request.Request("https://example.com/secure")
        with mock.patch.object(_http.socket, "getaddrinfo", return_value=public), \
             self.assertRaises(_http.BlockedURL) as raised:
            handler.redirect_request(
                req, None, 302, "Found", {}, "http://example.com/insecure"
            )
        self.assertIn("downgrade", str(raised.exception))

    def test_cross_origin_redirect_keeps_only_safe_headers(self):
        public = [(2, 1, 6, "", ("93.184.216.34", 443))]
        handler = _http._ValidatedRedirectHandler()
        req = _http.urllib.request.Request(
            "https://api.example.com/data",
            headers={
                "Authorization": "Bearer placeholder",
                "API-OPR": "private-value",
                "Cookie": "session=private-value",
                "Accept": "application/json",
                "User-Agent": "connector-test",
            },
        )
        with mock.patch.object(_http.socket, "getaddrinfo", return_value=public):
            redirected = handler.redirect_request(
                req, None, 302, "Found", {}, "https://other.example.com/data"
            )
        lowered = {key.lower(): value for key, value in redirected.header_items()}
        self.assertEqual(lowered["accept"], "application/json")
        self.assertEqual(lowered["user-agent"], "connector-test")
        self.assertNotIn("authorization", lowered)
        self.assertNotIn("api-opr", lowered)
        self.assertNotIn("cookie", lowered)

    def test_same_origin_redirect_retains_headers(self):
        public = [(2, 1, 6, "", ("93.184.216.34", 443))]
        handler = _http._ValidatedRedirectHandler()
        req = _http.urllib.request.Request(
            "https://example.com/one", headers={"Authorization": "Bearer placeholder"}
        )
        with mock.patch.object(_http.socket, "getaddrinfo", return_value=public):
            redirected = handler.redirect_request(
                req, None, 302, "Found", {}, "https://example.com/two"
            )
        self.assertEqual(redirected.get_header("Authorization"), "Bearer placeholder")

    def test_connection_phase_blocks_dns_rebinding_before_socket_open(self):
        public = [(2, 1, 6, "", ("93.184.216.34", 80))]
        rebound = [(2, 1, 6, "", ("127.0.0.1", 80))]
        with mock.patch.object(_http.socket, "getaddrinfo", side_effect=[public, rebound]), \
             mock.patch.object(_http.socket, "socket") as socket_factory, \
             mock.patch.object(_http.time, "sleep") as sleep:
            result = _http.get("http://rebind.test/", retries=3)
        self.assertIn("non-public", result["error"])
        socket_factory.assert_not_called()
        sleep.assert_not_called()

    def test_pinned_connection_uses_validated_ip_without_second_dns_lookup(self):
        public = [(2, 1, 6, "", ("93.184.216.34", 443))]
        sock = mock.Mock()
        with mock.patch.object(_http.socket, "getaddrinfo", return_value=public) as resolve, \
             mock.patch.object(_http.socket, "socket", return_value=sock):
            connected = _http._create_pinned_connection(("example.com", 443), timeout=2)
        self.assertIs(connected, sock)
        resolve.assert_called_once_with("example.com", 443, type=_http.socket.SOCK_STREAM)
        sock.connect.assert_called_once_with(("93.184.216.34", 443))

    def test_connector_opener_disables_ambient_proxy_resolution(self):
        public = [(2, 1, 6, "", ("93.184.216.34", 443))]
        opener = mock.Mock()
        opener.open.side_effect = _http.urllib.error.URLError("offline")
        with mock.patch.object(_http.socket, "getaddrinfo", return_value=public), \
             mock.patch.object(_http.urllib.request, "build_opener", return_value=opener) as build:
            _http.get("https://example.com/", retries=1)
        proxy_handler = build.call_args.args[0]
        self.assertIsInstance(proxy_handler, _http.urllib.request.ProxyHandler)
        self.assertEqual(proxy_handler.proxies, {})

    def test_gzip_decode_is_output_bounded(self):
        import gzip

        compressed = gzip.compress(b"x" * 1_000_000)
        body, truncated, error = _http.decompress_gzip(compressed, 1024)
        self.assertEqual(len(body), 1024)
        self.assertTrue(truncated)
        self.assertIsNone(error)

    def test_gzip_decode_supports_concatenated_members(self):
        import gzip

        compressed = gzip.compress(b"first-") + gzip.compress(b"second")
        body, truncated, error = _http.decompress_gzip(compressed, 1024)
        self.assertEqual(body, b"first-second")
        self.assertFalse(truncated)
        self.assertIsNone(error)

    def test_gzip_decode_rejects_truncated_footer(self):
        import gzip

        compressed = gzip.compress(b"complete payload")[:-4]
        body, truncated, error = _http.decompress_gzip(compressed, 1024)
        self.assertTrue(error)
        self.assertFalse(truncated)
        self.assertNotEqual(body, b"complete payload")

    def test_gzip_decode_rejects_empty_truncated_stream(self):
        body, truncated, error = _http.decompress_gzip(b"", 1024)
        self.assertEqual(body, b"")
        self.assertFalse(truncated)
        self.assertIn("truncated", error)

    def test_gzip_validates_corrupt_footer_after_output_cap(self):
        import gzip

        compressed = bytearray(gzip.compress(b"x" * 1_000_000))
        compressed[-1] ^= 0xFF
        body, truncated, error = _http.decompress_gzip(bytes(compressed), 1024)
        self.assertEqual(body, b"")
        self.assertFalse(truncated)
        self.assertIn("invalid gzip", error)

    def test_gzip_rejects_unvalidated_work_beyond_hard_ceiling(self):
        import gzip

        compressed = gzip.compress(b"x" * 10_000)
        body, truncated, error = _http.decompress_gzip(
            compressed, 1024, max_validation_bytes=2048
        )
        self.assertEqual(body, b"")
        self.assertFalse(truncated)
        self.assertIn("work limit", error)

    def test_gzip_reports_expanded_work_even_when_validation_cap_rejects(self):
        import gzip

        compressed = gzip.compress(b"x" * 10_000)
        body, truncated, error, work = _http.decompress_gzip(
            compressed,
            1024,
            max_validation_bytes=2048,
            return_work=True,
        )
        self.assertEqual(body, b"")
        self.assertFalse(truncated)
        self.assertIn("work limit", error)
        self.assertEqual(work, 2048)

    def test_process_deadline_terminates_a_blocked_response_read(self):
        class SlowHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                time.sleep(1.0)
                try:
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b"<urlset />")
                except (BrokenPipeError, ConnectionResetError):
                    pass

            def log_message(self, format, *args):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), SlowHandler)
        server.daemon_threads = True
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        before_children = {child.pid for child in _http.multiprocessing.active_children()}
        started = time.monotonic()
        try:
            response = _http.get_hard_deadline(
                "http://127.0.0.1:%d/sitemap.xml" % server.server_port,
                deadline=started + 0.35,
                allow_private=True,
                retries=1,
                timeout=10,
            )
            elapsed = time.monotonic() - started
        finally:
            server.shutdown()
            server.server_close()
        self.assertTrue(response["deadline_exceeded"])
        self.assertTrue(response["truncated"])
        self.assertIn("deadline", response["error"])
        self.assertLess(elapsed, 0.75)
        after_children = {child.pid for child in _http.multiprocessing.active_children()}
        self.assertEqual(after_children - before_children, set())

    def test_retry_after_wait_is_capped(self):
        streams = [io.BytesIO(), io.BytesIO()]
        errors = [
            _http.urllib.error.HTTPError(
                "https://example.com/", 429, "rate limited",
                {"Retry-After": "999"}, stream
            )
            for stream in streams
        ]
        opener = mock.Mock()
        opener.open.side_effect = errors
        public = [(2, 1, 6, "", ("93.184.216.34", 443))]
        with mock.patch.object(_http.socket, "getaddrinfo", return_value=public), \
             mock.patch.object(_http.urllib.request, "build_opener", return_value=opener), \
             mock.patch.object(_http.time, "sleep") as sleep:
            result = _http.get("https://example.com/", retries=2, max_retry_after=3)
        sleep.assert_called_once_with(3)
        self.assertEqual(result["status"], 429)
        self.assertTrue(all(stream.closed for stream in streams))

    def test_retry_after_header_lookup_is_case_insensitive(self):
        # Python 3.9's HTTPError response methods proxy through ``fp`` and may
        # raise while handling a perfectly valid synthetic ``fp=None`` error.
        # The connector must still preserve the status/header retry behavior.
        error = _http.urllib.error.HTTPError(
            "https://example.com/", 503, "unavailable", {"retry-after": "9"}, None
        )
        opener = mock.Mock()
        opener.open.side_effect = [error, _http.urllib.error.URLError("offline")]
        public = [(2, 1, 6, "", ("93.184.216.34", 443))]
        with mock.patch.object(_http.socket, "getaddrinfo", return_value=public), \
             mock.patch.object(_http.urllib.request, "build_opener", return_value=opener), \
             mock.patch.object(_http.time, "sleep") as sleep:
            _http.get("https://example.com/", retries=2, max_retry_after=30)
        sleep.assert_called_once_with(9)


class SitemapBudgetTests(unittest.TestCase):
    ROOT_URL = "https://example.com/root.xml"

    @staticmethod
    def _index(*children):
        locs = "".join("<sitemap><loc>%s</loc></sitemap>" % child for child in children)
        return ("<sitemapindex>%s</sitemapindex>" % locs).encode()

    @staticmethod
    def _urlset(loc):
        return ("<urlset><url><loc>%s</loc></url></urlset>" % loc).encode()

    def _fetcher(self, bodies, calls):
        def fetch(url, **kwargs):
            calls.append((url, kwargs))
            full = bodies[url]
            cap = kwargs.get("max_bytes", len(full))
            return {
                "status": 200,
                "url": url,
                "headers": {},
                "body": full[:cap],
                "error": None,
                "truncated": len(full) > cap,
            }
        return fetch

    def test_transport_final_url_is_authoritative(self):
        response = {
            "status": 200,
            "url": "https://cdn.example.com/final.xml.gz",
            "headers": {},
            "body": b"payload",
            "error": None,
            "truncated": False,
        }
        with mock.patch.object(sitemap._http, "get", return_value=response), \
             mock.patch.object(sitemap._http, "redirect_safety_error", return_value=None):
            result = sitemap._get_following("https://example.com/start")
        self.assertEqual(result["final_url"], response["url"])

    def test_transport_final_url_cannot_bypass_downgrade_policy(self):
        response = {
            "status": 200,
            "url": "http://example.com/final.xml",
            "headers": {},
            "body": b"<urlset />",
            "error": None,
            "truncated": False,
        }
        with mock.patch.object(sitemap._http, "get", return_value=response):
            result = sitemap._get_following("https://example.com/start")
        self.assertEqual(result["status"], 0)
        self.assertIn("downgrade", result["error"])

    def test_collect_classifies_using_transport_final_url(self):
        response = {
            "status": 200,
            "url": "https://cdn.example.com/llms.txt",
            "headers": {},
            "body": b"https://example.com/from-llms\n",
            "error": None,
            "truncated": False,
        }
        with mock.patch.object(sitemap._http, "get", return_value=response), \
             mock.patch.object(sitemap._http, "redirect_safety_error", return_value=None):
            result = sitemap.collect("https://example.com/start.xml")
        self.assertEqual(result["type"], "llms.txt")
        self.assertEqual(result["urls"][0]["loc"], "https://example.com/from-llms")

    def test_collect_classifies_llms_path_with_query_string(self):
        response = {
            "status": 200,
            "url": "https://cdn.example.com/llms.txt?v=1",
            "headers": {},
            "body": b"https://example.com/from-versioned-llms\n",
            "error": None,
            "truncated": False,
        }
        with mock.patch.object(sitemap._http, "get", return_value=response), \
             mock.patch.object(sitemap._http, "redirect_safety_error", return_value=None):
            result = sitemap.collect("https://example.com/start.xml")
        self.assertEqual(result["type"], "llms.txt")
        self.assertEqual(
            result["urls"][0]["loc"],
            "https://example.com/from-versioned-llms",
        )

    def test_manual_redirect_rejects_https_downgrade_before_second_hop(self):
        calls = []

        def redirect(url, **kwargs):
            calls.append(url)
            return {
                "status": 302,
                "url": url,
                "headers": {"location": "http://example.com/insecure.xml"},
                "body": b"",
                "error": "HTTP 302",
                "truncated": False,
            }

        with mock.patch.object(sitemap._http, "get", side_effect=redirect):
            result = sitemap._get_following("https://example.com/start.xml")
        self.assertEqual(len(calls), 1)
        self.assertEqual(result["status"], 0)
        self.assertIn("downgrade", result["error"])

    def test_manual_redirect_parent_never_performs_unbounded_dns(self):
        calls = []

        def request(url, **kwargs):
            calls.append(url)
            if len(calls) == 1:
                return {
                    "status": 302,
                    "url": url,
                    "headers": {"Location": "https://private.invalid/next.xml"},
                    "body": b"",
                    "error": "HTTP 302",
                    "truncated": False,
                }
            # Production request_hop performs this full target validation in
            # its terminable child before any socket is opened.
            return {
                "status": 0,
                "url": url,
                "headers": {},
                "body": b"",
                "error": "blocked non-public destination",
                "truncated": False,
            }

        with mock.patch.object(
            sitemap._http.socket,
            "getaddrinfo",
            side_effect=AssertionError("parent DNS must not run"),
        ):
            result = sitemap._get_following(
                "https://example.com/start.xml",
                request=request,
                deadline=time.monotonic() + 1.0,
            )
        self.assertEqual(len(calls), 2)
        self.assertEqual(result["status"], 0)
        self.assertIn("non-public", result["error"])

    def test_global_queue_budget_caps_nested_work(self):
        children = ["https://example.com/%d.xml" % i for i in range(3)]
        bodies = {self.ROOT_URL: self._index(*children)}
        bodies.update({child: self._urlset(child + "/page") for child in children})
        calls = []
        with mock.patch.object(sitemap._http, "get",
                               side_effect=self._fetcher(bodies, calls)):
            result = sitemap.collect(self.ROOT_URL, max_queue=2, max_fetches=10)
        self.assertEqual([error["error"] for error in result["errors"]].count(
            "global queue budget exhausted"), 1)
        self.assertTrue(result["truncated"])
        self.assertLessEqual(len(calls), 2)

    def test_global_fetch_budget_caps_nested_work(self):
        children = ["https://example.com/%d.xml" % i for i in range(3)]
        bodies = {self.ROOT_URL: self._index(*children)}
        bodies.update({child: self._urlset(child + "/page") for child in children})
        calls = []
        with mock.patch.object(sitemap._http, "get",
                               side_effect=self._fetcher(bodies, calls)):
            result = sitemap.collect(self.ROOT_URL, max_queue=10, max_fetches=2)
        self.assertEqual(len(calls), 2)
        self.assertIn("global fetch budget exhausted",
                      [error["error"] for error in result["errors"]])

    def test_global_byte_budget_is_shared_across_documents(self):
        child = "https://example.com/child.xml"
        root_body = self._index(child)
        bodies = {
            self.ROOT_URL: root_body,
            child: self._urlset("https://example.com/a-page"),
        }
        calls = []
        with mock.patch.object(sitemap._http, "get",
                               side_effect=self._fetcher(bodies, calls)):
            result = sitemap.collect(
                self.ROOT_URL,
                max_queue=10,
                max_fetches=10,
                max_total_bytes=len(root_body) + 12,
            )
        self.assertIn("global byte budget exhausted",
                      [error["error"] for error in result["errors"]])
        self.assertLessEqual(result["budget"]["bytes_used"], len(root_body) + 12)

    def test_literal_gzip_truncation_propagates_to_global_byte_budget(self):
        import gzip

        target = "https://example.com/root.xml.gz"
        expanded = self._urlset("https://example.com/page") + b" " * 10_000
        bodies = {target: gzip.compress(expanded)}
        calls = []
        with mock.patch.object(sitemap._http, "get",
                               side_effect=self._fetcher(bodies, calls)):
            result = sitemap.collect(target, max_total_bytes=1024)
        self.assertTrue(result["truncated"])
        self.assertEqual(result["budget"]["bytes_used"], 1024)
        self.assertIn("global byte budget exhausted",
                      [error["error"] for error in result["errors"]])

    def test_gzip_validation_work_budget_is_shared_across_bombs(self):
        import gzip

        children = ["https://example.com/one.xml.gz",
                    "https://example.com/two.xml.gz"]
        root = self._index(*children)
        first_expanded = self._urlset("https://example.com/one") + b" " * 1800
        second_expanded = self._urlset("https://example.com/two") + b" " * 1800
        work_budget = len(first_expanded) + 127
        bodies = {
            self.ROOT_URL: root,
            children[0]: gzip.compress(first_expanded),
            children[1]: gzip.compress(second_expanded),
        }
        calls = []
        with mock.patch.object(sitemap._http, "get",
                               side_effect=self._fetcher(bodies, calls)):
            result = sitemap.collect(
                self.ROOT_URL,
                max_fetches=10,
                max_total_bytes=100_000,
                max_gzip_work=work_budget,
            )
        self.assertEqual(len(calls), 3)
        self.assertEqual(result["budget"]["gzip_work_used"], work_budget)
        self.assertTrue(result["truncated"])
        self.assertIn(
            "global gzip work budget exhausted",
            [error["error"] for error in result["errors"]],
        )
        self.assertNotIn(
            "global byte budget exhausted",
            [error["error"] for error in result["errors"]],
        )
        self.assertTrue(any(
            "validation work limit exceeded" in error["error"]
            for error in result["errors"]
        ))

    def test_transport_plus_literal_gzip_work_does_not_misreport_byte_exhaustion(self):
        import gzip

        target = "https://example.com/double.xml.gz"
        expanded = self._urlset("https://example.com/page") + b" " * 5000
        inner = gzip.compress(expanded)
        outer = gzip.compress(inner)
        response = {
            "status": 200,
            "url": target,
            "headers": {},
            # This is the literal gzip layer left after transport decoding.
            "body": inner,
            "error": None,
            "truncated": False,
            "transport_bytes": len(outer),
            "gzip_expanded_bytes": len(inner),
        }
        work_budget = len(inner) + 127
        with mock.patch.object(sitemap._http, "get", return_value=response):
            result = sitemap.collect(
                target,
                max_total_bytes=100_000,
                max_gzip_work=work_budget,
            )
        errors = [entry["error"] for entry in result["errors"]]
        self.assertEqual(result["budget"]["gzip_work_used"], work_budget)
        self.assertLess(result["budget"]["bytes_used"], 100_000)
        self.assertIn("global gzip work budget exhausted", errors)
        self.assertNotIn("global byte budget exhausted", errors)

    def test_gzip_suffix_does_not_double_decode_transport_decoded_xml(self):
        target = "https://example.com/root.xml.gz"
        xml = self._urlset("https://example.com/page")
        bodies = {target: xml}
        calls = []
        with mock.patch.object(sitemap._http, "get",
                               side_effect=self._fetcher(bodies, calls)):
            result = sitemap.collect(target)
        self.assertEqual(result["url_count"], 1)
        self.assertEqual(result["urls"][0]["loc"], "https://example.com/page")

    def test_global_time_budget_stops_after_slow_fetch(self):
        bodies = {self.ROOT_URL: self._urlset("https://example.com/page")}
        calls = []
        clock = [0.0]
        fetcher = self._fetcher(bodies, calls)

        def slow_fetch(url, **kwargs):
            response = fetcher(url, **kwargs)
            clock[0] = 2.0
            return response

        with mock.patch.object(sitemap._http, "get", side_effect=slow_fetch), \
             mock.patch.object(sitemap.time, "monotonic", side_effect=lambda: clock[0]):
            result = sitemap.collect(self.ROOT_URL, max_seconds=1.0)
        self.assertIn("global time budget exhausted",
                      [error["error"] for error in result["errors"]])
        self.assertTrue(result["truncated"])

    def test_deadline_prevents_a_second_redirect_fetch(self):
        calls = []
        clock = [0.0]

        def slow_redirect(url, **kwargs):
            calls.append((url, kwargs["timeout"], kwargs["follow_redirects"]))
            clock[0] = 2.0
            return {
                "status": 302,
                "url": url,
                "headers": {"Location": "https://example.com/next.xml"},
                "body": b"",
                "error": "HTTP 302",
                "truncated": False,
            }

        with mock.patch.object(sitemap._http, "get", side_effect=slow_redirect), \
             mock.patch.object(sitemap._http, "redirect_safety_error", return_value=None), \
             mock.patch.object(sitemap.time, "monotonic", side_effect=lambda: clock[0]):
            result = sitemap.collect(self.ROOT_URL, max_seconds=1.0)
        self.assertEqual(len(calls), 1)
        self.assertFalse(calls[0][2])
        self.assertLessEqual(calls[0][1], 1.0)
        self.assertIn("global time budget exhausted",
                      [error["error"] for error in result["errors"]])


class MissingConnectorCoverageTests(unittest.TestCase):
    """Keep every bundled connector module under an offline parser/builder test."""

    def test_every_bundled_connector_module_is_loaded_by_this_suite(self):
        connector_dir = ROOT / "scripts" / "connectors"
        expected = {path.stem for path in connector_dir.glob("*.py")}
        loaded = {
            pathlib.Path(module.__file__).stem
            for module in globals().values()
            if getattr(module, "__file__", None)
            and pathlib.Path(module.__file__).resolve().parent == connector_dir.resolve()
        }
        self.assertEqual(loaded, expected)

    def test_kg_search_builds_a_bounded_encoded_request_and_parses_results(self):
        response = {
            "status": 200,
            "error": None,
            "json": {"search": [{
                "id": "Q1", "label": "A & B", "description": "fixture",
                "match": {"text": "A & B"},
            }]},
        }
        with mock.patch.object(kg._http, "get_json", return_value=response) as get_json:
            result = kg.search("A & B", lang="en", limit=999)
        request_url = get_json.call_args.args[0]
        self.assertIn("search=A+%26+B", request_url)
        self.assertIn("limit=50", request_url)
        self.assertEqual(result["candidates"][0]["qid"], "Q1")
        self.assertEqual(
            kg._snak_value({
                "snaktype": "value",
                "datavalue": {"value": {"id": "Q42"}},
            }),
            "Q42",
        )

    def test_crawl_normalizes_and_parses_one_same_host_page_offline(self):
        response = {
            "status": 200,
            "url": "https://example.com/start",
            "headers": {"Content-Type": "text/html"},
            "text": (
                "<html><head><title> Fixture Page </title></head><body>"
                '<a href="/inside#part">inside</a>'
                '<a href="https://other.example/out">outside</a>'
                "</body></html>"
            ),
            "error": None,
        }
        with mock.patch.object(crawl._http, "get_text", return_value=response):
            rows = crawl.crawl(
                "https://example.com/start#fragment",
                max_pages=1,
                max_depth=1,
                respect_robots=False,
                delay=0,
            )
        self.assertEqual(rows[0]["url"], "https://example.com/start")
        self.assertEqual(rows[0]["title"], "Fixture Page")
        self.assertEqual(rows[0]["links_out"], ["https://example.com/inside"])
        self.assertTrue(crawl.same_host("https://EXAMPLE.com/a", "example.com"))

    def test_rss_monitor_parses_rss_and_atom_without_network(self):
        rss = (
            "<rss><channel><title>Fixture RSS</title><item>"
            "<title>One</title><link>https://example.com/one</link>"
            "<pubDate>today</pubDate><description>Summary</description>"
            "</item></channel></rss>"
        )
        items, title = rss_monitor.parse_feed(rss)
        self.assertEqual(title, "Fixture RSS")
        self.assertEqual(items[0]["link"], "https://example.com/one")
        atom = (
            '<feed xmlns="http://www.w3.org/2005/Atom"><title>Fixture Atom</title>'
            '<entry><title>Two</title><link rel="alternate" '
            'href="https://example.com/two"/><updated>now</updated></entry></feed>'
        )
        atom_items, atom_title = rss_monitor.parse_feed(atom)
        self.assertEqual(atom_title, "Fixture Atom")
        self.assertEqual(atom_items[0]["link"], "https://example.com/two")

    def test_suggest_request_builder_and_shape_parser(self):
        request_url = suggest.build_query("seo audit", hl="en", gl="US")
        self.assertIn("client=firefox", request_url)
        self.assertIn("q=seo+audit", request_url)
        self.assertEqual(
            suggest.parse_suggestions(["seo", ["SEO audit", 42, "seo tools"]]),
            ["SEO audit", "seo tools"],
        )
        self.assertEqual(suggest.parse_suggestions({"unexpected": "shape"}), [])

    def test_wayback_request_builder_and_cdx_parser(self):
        request_url, params = wayback.build_query(
            "example.com/docs", match="prefix", limit=2,
            from_date="20260101", to_date="20261231",
        )
        self.assertIn("output=json", request_url)
        self.assertEqual(params["url"], "example.com/docs/*")
        rows = [
            ["timestamp", "original", "statuscode", "mimetype", "digest"],
            ["20260101000000", "https://example.com/a", "200", "text/html", "one"],
            ["20260201000000", "https://example.com/b", "404"],
        ]
        records = wayback.parse_cdx_rows(rows)
        self.assertIsNone(records[1]["mimetype"])
        summary = wayback.summarize(records)
        self.assertEqual(summary["total_captures"], 2)
        self.assertEqual(summary["status_codes"], {"200": 1, "404": 1})

class OnPageParserTests(unittest.TestCase):
    def test_word_count_excludes_non_visible_head_and_script_text(self):
        html = """<!doctype html>
        <html>
          <head>
            <title>Invisible title</title>
            <style>.hidden words should not count</style>
            <script>var fake = "many invisible words here";</script>
          </head>
          <body>
            <h1>Hello world</h1>
            <p>Visible text only.</p>
          </body>
        </html>"""

        result = onpage.analyze(html)

        self.assertEqual(result["title"], "Invisible title")
        self.assertEqual(result["headings"]["h1"], ["Hello world"])
        self.assertEqual(result["word_count"], 5)


class LinkGraphTests(unittest.TestCase):
    def test_analyze_deduplicates_internal_links_and_reports_orphans(self):
        pages = [
            {
                "url": "https://example.com/",
                "depth": 0,
                "title": "Home",
                "links_out": [
                    "https://example.com/a",
                    "https://example.com/a",
                    "https://external.test/",
                ],
            },
            {
                "url": "https://example.com/a",
                "depth": 1,
                "title": "A",
                "links_out": [],
            },
            {
                "url": "https://example.com/orphan",
                "depth": 2,
                "title": "Orphan",
                "links_out": [],
            },
        ]

        result = linkgraph.analyze(pages)

        self.assertEqual(result["summary"]["total_internal_links"], 1)
        self.assertEqual(result["degrees"]["https://example.com/a"]["in"], 1)
        self.assertEqual(result["orphans"], ["https://example.com/orphan"])


class SchemaLintTests(unittest.TestCase):
    def test_lint_html_reports_required_schema_errors(self):
        html = """<script type="application/ld+json">
        {"@context":"https://schema.org","@type":"Article"}
        </script>"""

        result = schema_lint.lint_html(html, source="<test>")

        self.assertEqual(result["summary"]["errors"], 1)
        self.assertEqual(result["objects"][0]["@type"], "Article")
        self.assertEqual(result["objects"][0]["missing_required"], ["headline"])


class RobotsTxtTests(unittest.TestCase):
    def _parse(self, text):
        return robots.RobotsTxt.parse(text, "https://example.com/robots.txt", 200, None)

    def test_longest_match_wins_and_allow_beats_disallow(self):
        r = self._parse("User-agent: *\nDisallow: /admin\nAllow: /admin/public\n")
        # shorter Disallow /admin blocks a path with no longer match
        self.assertFalse(r.can_fetch("mybot", "/admin/secret")[0])
        # longer Allow /admin/public wins over the shorter Disallow
        self.assertTrue(r.can_fetch("mybot", "/admin/public/page")[0])
        # no rule matches -> default-allow
        self.assertTrue(r.can_fetch("mybot", "/blog/post")[0])

    def test_wildcard_and_end_anchor(self):
        r = self._parse("User-agent: *\nDisallow: /*.pdf$\n")
        self.assertFalse(r.can_fetch("mybot", "/files/report.pdf")[0])
        # the $ anchor means a query-suffixed path no longer matches -> allowed
        self.assertTrue(r.can_fetch("mybot", "/files/report.pdf?x=1")[0])


class PsiGradeTests(unittest.TestCase):
    def test_lcp_threshold_boundaries(self):
        self.assertEqual(psi.grade("LCP_ms", 2500.0), "good")            # <= good_max
        self.assertEqual(psi.grade("LCP_ms", 2500.1), "needs-improvement")
        self.assertEqual(psi.grade("LCP_ms", 4000.0), "needs-improvement")  # <= ni_max
        self.assertEqual(psi.grade("LCP_ms", 4000.1), "poor")

    def test_cls_none_and_unknown_metric(self):
        self.assertEqual(psi.grade("CLS", 0.1), "good")
        self.assertEqual(psi.grade("CLS", 0.26), "poor")
        self.assertIsNone(psi.grade("LCP_ms", None))
        self.assertIsNone(psi.grade("not_a_metric", 1.0))


class LedgerTests(unittest.TestCase):
    def test_slugify_normalizes_collapses_and_defaults(self):
        self.assertEqual(ledger.slugify("https://www.Example.com/path/"), "www.example.com-path")
        self.assertEqual(ledger.slugify("HTTP://a//b"), "a-b")
        self.assertEqual(ledger.slugify("   "), "unnamed")

    def test_flatten_dotted_keys_and_list_indices(self):
        flat = ledger.flatten({"a": {"b": 1}, "c": [10, 20]})
        self.assertEqual(flat["a.b"], 1)
        self.assertEqual(flat["c[0]"], 10)
        self.assertEqual(flat["c[1]"], 20)


class OpenPageRankTests(unittest.TestCase):
    def test_normalize_domain(self):
        self.assertEqual(openpagerank.normalize_domain("https://www.Example.com/path"), "www.example.com")
        self.assertEqual(openpagerank.normalize_domain("Example.com/foo"), "example.com")
        self.assertEqual(openpagerank.normalize_domain(""), "")

    def test_parse_response_maps_onto_requested_order(self):
        payload = {"status_code": 200, "response": [
            {"domain": "b.com", "page_rank_decimal": 5.1, "page_rank_integer": 5,
             "rank": "100", "status_code": 200},
        ]}
        rows = openpagerank.parse_response(payload, ["a.com", "b.com"])
        self.assertEqual([r["domain"] for r in rows], ["a.com", "b.com"])
        self.assertFalse(rows[0]["found"])   # a.com absent from response
        self.assertTrue(rows[1]["found"])    # b.com present with status 200
        self.assertEqual(rows[1]["page_rank_decimal"], 5.1)


class ResendSpecTests(unittest.TestCase):
    def _spec(self, argv):
        return resend.build_spec(resend.build_parser().parse_args(argv))

    def test_read_commands_are_not_mutating(self):
        for argv in (["domains"], ["contacts"], ["segments"], ["broadcasts"],
                     ["emails", "--limit", "5"]):
            spec = self._spec(argv)
            self.assertFalse(spec["mutating"], argv)
            self.assertEqual(spec["request"]["method"], "GET")

    def test_every_send_path_is_flagged_mutating(self):
        send = ["send", "--from", "me@x.dev", "--to", "a@y.com",
                "--subject", "s", "--text", "body text"]
        for argv in (send, ["verify-domain", "d1"], ["suppress", "a@y.com"],
                     ["cancel-email", "e1"], ["broadcast-send", "b1"]):
            self.assertTrue(self._spec(argv)["mutating"], argv)

    def test_seed_expands_one_message_per_recipient(self):
        spec = self._spec(["seed", "--from", "me@x.dev",
                           "--to", "s1@gmail.com, s2@outlook.com",
                           "--subject", "seed", "--text", "plain body"])
        body = spec["request"]["body"]
        self.assertEqual(spec["request"]["url"], resend.API_BASE + "/emails/batch")
        self.assertEqual([m["to"] for m in body], [["s1@gmail.com"], ["s2@outlook.com"]])

    def test_send_requires_content_and_recipients(self):
        base = ["send", "--from", "me@x.dev", "--subject", "s"]
        self.assertEqual(self._spec(base + ["--to", "a@y.com"])["error"],
                         "missing_content")
        self.assertEqual(self._spec(base + ["--to", " ", "--text", "t"])["error"],
                         "no_recipients")

    def test_suppress_quotes_email_in_path_and_sets_unsubscribed(self):
        spec = self._spec(["suppress", "jane@example.com"])
        self.assertEqual(spec["request"]["url"],
                         resend.API_BASE + "/contacts/jane%40example.com")
        self.assertEqual(spec["request"]["method"], "PATCH")
        self.assertEqual(spec["request"]["body"], {"unsubscribed": True})

    def test_sends_carry_idempotency_key_but_non_supporting_calls_do_not(self):
        send = ["send", "--from", "me@x.dev", "--to", "a@y.com",
                "--subject", "s", "--text", "t"]
        seed = ["seed", "--from", "me@x.dev", "--to", "a@y.com",
                "--subject", "s", "--text", "t"]
        for argv in (send, seed):
            hdrs = self._spec(argv)["request"]["headers"]
            self.assertTrue(hdrs["Idempotency-Key"].startswith("resend-py/"), argv)
        # No Idempotency-Key on endpoints Resend does not support it for.
        for argv in (["suppress", "a@y.com"], ["broadcast-send", "b1"],
                     ["verify-domain", "d1"]):
            self.assertEqual(self._spec(argv)["request"]["headers"], {}, argv)

    def test_explicit_idempotency_key_is_used_and_capped(self):
        spec = self._spec(["send", "--from", "me@x.dev", "--to", "a@y.com",
                           "--subject", "s", "--text", "t",
                           "--idempotency-key", "welcome/123"])
        self.assertEqual(spec["request"]["headers"]["Idempotency-Key"], "welcome/123")
        self.assertEqual(len(resend.idempotency_key("x" * 400)),
                         resend.IDEMPOTENCY_MAX)

    def test_broadcast_create_bad_content_returns_error_not_traceback(self):
        spec = self._spec(["broadcast-create", "--segment", "seg_1",
                           "--from", "me@x.dev", "--subject", "s",
                           "--html", "no-such-file.html"])
        self.assertEqual(spec["error"], "bad_content")
        self.assertIn("no-such-file.html", spec["detail"])

    def test_broadcast_create_happy_path(self):
        spec = self._spec(["broadcast-create", "--segment", "seg_1",
                           "--from", "me@x.dev", "--subject", "s",
                           "--text", "body text"])
        self.assertTrue(spec["mutating"])
        body = spec["request"]["body"]
        self.assertEqual(body["segment_id"], "seg_1")
        self.assertEqual(body["text"], "body text")


class FirecrawlSpecTests(unittest.TestCase):
    def _spec(self, argv):
        return firecrawl.build_spec(firecrawl.build_parser().parse_args(argv))

    def test_scrape_body_and_preflight_target(self):
        spec = self._spec(["scrape", "https://x.dev/p", "--formats",
                           "markdown, links", "--wait", "1500", "--full-page"])
        self.assertEqual(spec["target"], "https://x.dev/p")
        self.assertEqual(spec["request"]["body"], {
            "url": "https://x.dev/p", "formats": ["markdown", "links"],
            "onlyMainContent": False, "waitFor": 1500})

    def test_search_has_no_preflight_target_and_splits_domains(self):
        spec = self._spec(["search", "best crm", "--limit", "5", "--scrape",
                           "--include-domains", "a.com, b.com"])
        self.assertIsNone(spec["target"])
        body = spec["request"]["body"]
        self.assertEqual(body["includeDomains"], ["a.com", "b.com"])
        self.assertEqual(body["scrapeOptions"], {"formats": ["markdown"]})

    def test_crawl_job_endpoints(self):
        start = self._spec(["crawl", "https://x.dev", "--limit", "50"])
        self.assertEqual(start["request"]["body"]["limit"], 50)
        self.assertEqual(start["target"], "https://x.dev")
        status = self._spec(["crawl-status", "job/1"])
        self.assertEqual(status["request"]["method"], "GET")
        self.assertEqual(status["request"]["url"],
                         firecrawl.API_BASE + "/crawl/job%2F1")
        self.assertIsNone(status["target"])

    def test_preflight_refuses_on_disallow_and_allows_otherwise(self):
        parsed = robots_mod.RobotsTxt.parse(
            "User-agent: *\nDisallow: /private\n",
            "https://x.dev/robots.txt", 200, None)
        original = firecrawl.robots.fetch
        firecrawl.robots.fetch = lambda url: parsed
        try:
            self.assertFalse(firecrawl.preflight("https://x.dev/private/a")["allowed"])
            self.assertTrue(firecrawl.preflight("https://x.dev/public")["allowed"])
        finally:
            firecrawl.robots.fetch = original


class TavilySpecTests(unittest.TestCase):
    def _spec(self, argv):
        return tavily.build_spec(tavily.build_parser().parse_args(argv))

    def test_search_body_and_no_preflight_targets(self):
        spec = self._spec(["search", "topic q", "--limit", "10", "--answer",
                           "--topic", "news", "--time-range", "w",
                           "--include-domains", "a.com, b.com"])
        self.assertEqual(spec["targets"], [])
        body = spec["request"]["body"]
        self.assertEqual(body["max_results"], 10)
        self.assertEqual(body["include_answer"], True)
        self.assertEqual(body["topic"], "news")
        self.assertEqual(body["include_domains"], ["a.com", "b.com"])

    def test_answer_level_passthrough(self):
        body = self._spec(["search", "q", "--answer", "advanced"])["request"]["body"]
        self.assertEqual(body["include_answer"], "advanced")

    def test_extract_targets_and_url_shape(self):
        one = self._spec(["extract", "https://x.dev/a"])
        self.assertEqual(one["request"]["body"]["urls"], "https://x.dev/a")
        self.assertEqual(one["targets"], ["https://x.dev/a"])
        many = self._spec(["extract", "https://x.dev/a", "https://y.dev/b"])
        self.assertEqual(many["request"]["body"]["urls"],
                         ["https://x.dev/a", "https://y.dev/b"])
        self.assertEqual(len(many["targets"]), 2)

    def test_extract_preflight_blocks_on_disallow(self):
        parsed = robots_mod.RobotsTxt.parse(
            "User-agent: *\nDisallow: /private\n",
            "https://x.dev/robots.txt", 200, None)
        original = tavily.robots.fetch
        tavily.robots.fetch = lambda url: parsed
        try:
            self.assertFalse(tavily.preflight("https://x.dev/private/a")["allowed"])
            self.assertTrue(tavily.preflight("https://x.dev/ok")["allowed"])
        finally:
            tavily.robots.fetch = original


class DohTests(unittest.TestCase):
    def test_strip_txt_joins_chunked_quoted_payloads(self):
        self.assertEqual(doh._strip_txt('"v=DMARC1; p=no" "ne; rua=x"'),
                         "v=DMARC1; p=none; rua=x")
        self.assertEqual(doh._strip_txt("plain"), "plain")

    def test_parse_tags(self):
        tags = doh.parse_tags("v=DMARC1; p=none; rua=mailto:a@b; aspf=s")
        self.assertEqual(tags["p"], "none")
        self.assertEqual(tags["aspf"], "s")

    def test_spf_facts_flags(self):
        ok = doh.spf_facts(["v=spf1 include:_spf.x.com ~all"])
        self.assertTrue(ok["present"])
        self.assertEqual(ok["flags"], [])
        redirect = doh.spf_facts(["v=spf1 redirect=_spf.google.com"])
        self.assertEqual(redirect["flags"], [])
        open_ended = doh.spf_facts(["v=spf1 include:_spf.x.com"])
        self.assertIn("no_all_or_redirect", open_ended["flags"])
        double = doh.spf_facts(["v=spf1 ~all", "v=spf1 -all"])
        self.assertIn("multiple_spf_records", double["flags"])
        absent = doh.spf_facts(["some-verification=abc"])
        self.assertFalse(absent["present"])

    def test_build_url_per_resolver(self):
        self.assertIn("dns.google/resolve?", doh.build_url("_dmarc.x.com"))
        self.assertIn("cloudflare-dns.com", doh.build_url("x.com", "MX", "cloudflare"))


class PageviewsTests(unittest.TestCase):
    def test_build_url_encodes_title(self):
        url = pageviews.build_url("Claude (language model)/x")
        self.assertIn("Claude_%28language_model%29%2Fx", url)
        self.assertIn("/monthly/", url)

    def test_default_range_monthly_uses_full_months(self):
        start, end = pageviews.default_range(
            "monthly", months=3, today=_dt.date(2026, 7, 4))
        self.assertEqual(start, "2026040100")
        self.assertEqual(end, "2026063000")

    def test_default_range_daily_excludes_today(self):
        start, end = pageviews.default_range(
            "daily", days=7, today=_dt.date(2026, 7, 4))
        self.assertEqual(start, "2026062700")
        self.assertEqual(end, "2026070300")


class GdeltTests(unittest.TestCase):
    def test_build_url_params(self):
        url = gdelt.build_url('"acme corp"', "artlist", days=7, maxrecords=999)
        self.assertIn("timespan=7d", url)
        self.assertIn("maxrecords=%d" % gdelt.MAX_RECORDS, url)  # capped
        self.assertNotIn("maxrecords", gdelt.build_url("q", "timelinevol"))

    def test_parse_response_shapes(self):
        arts = gdelt.parse_response(
            {"articles": [{"title": "t", "url": "u", "domain": "d"}]}, "artlist")
        self.assertEqual(arts["count"], 1)
        self.assertEqual(arts["articles"][0]["domain"], "d")
        tl = gdelt.parse_response(
            {"timeline": [{"data": [{"date": "20260701", "value": 2}]}]},
            "timelinevol")
        self.assertEqual(tl["timeline"], [{"date": "20260701", "value": 2}])


class YoutubeSpecTests(unittest.TestCase):
    def test_parse_channel_ref_forms(self):
        self.assertEqual(youtube.parse_channel_ref("@mkbhd"), ("handle", "@mkbhd"))
        self.assertEqual(youtube.parse_channel_ref("mkbhd"), ("handle", "@mkbhd"))
        self.assertEqual(youtube.parse_channel_ref("UCBJycsmduvYEL83R_U4JriQ"),
                         ("id", "UCBJycsmduvYEL83R_U4JriQ"))
        self.assertEqual(
            youtube.parse_channel_ref(
                "https://www.youtube.com/channel/UCBJycsmduvYEL83R_U4JriQ"),
            ("id", "UCBJycsmduvYEL83R_U4JriQ"))
        self.assertEqual(youtube.parse_channel_ref("https://youtube.com/@mkbhd"),
                         ("handle", "@mkbhd"))

    def test_uploads_playlist_swap(self):
        self.assertEqual(youtube.uploads_playlist("UCabc123def456"), "UUabc123def456")
        self.assertIsNone(youtube.uploads_playlist("HCxyz"))


class IndexpushSpecTests(unittest.TestCase):
    def test_indexnow_requires_single_host_and_key(self):
        mixed = indexpush.build_spec("indexnow",
                                     ["https://a.com/1", "https://b.com/2"], key="k")
        self.assertEqual(mixed["error"], "mixed_or_missing_hosts")
        nokey = indexpush.build_spec("indexnow", ["https://a.com/1"])
        self.assertEqual(nokey["error"], "missing_key")

    def test_indexnow_body_shape(self):
        spec = indexpush.build_spec(
            "indexnow", ["https://a.com/1", "https://a.com/2"],
            key="abc123", key_location="https://a.com/abc123.txt")
        body = spec["request"]["body"]
        self.assertEqual(body["host"], "a.com")
        self.assertEqual(body["urlList"], ["https://a.com/1", "https://a.com/2"])
        self.assertEqual(body["keyLocation"], "https://a.com/abc123.txt")
        over = indexpush.build_spec(
            "indexnow", ["https://a.com/%d" % i for i in range(10_001)], key="k")
        self.assertEqual(over["error"], "too_many_urls")

    def test_baidu_spec(self):
        self.assertEqual(indexpush.build_spec("baidu", ["https://a.com/1"],
                                              key="t")["error"], "missing_site")
        spec = indexpush.build_spec("baidu", ["https://a.com/1"],
                                    key="tok", site="www.a.com")
        self.assertIn("site=www.a.com", spec["request"]["url"])
        self.assertIn("token=tok", spec["request"]["url"])
        self.assertEqual(spec["request"]["content_type"], "text/plain")
        self.assertEqual(spec["request"]["body"], ["https://a.com/1"])

    def test_collect_urls_dedupes_preserving_order(self):
        self.assertEqual(indexpush.collect_urls(["a", "b", "a", "c"], None),
                         ["a", "b", "c"])

    def execute_with_response(self, spec_request, response):
        original = indexpush._http.get_json
        indexpush._http.get_json = lambda *args, **kwargs: response
        try:
            return indexpush.execute(spec_request)
        finally:
            indexpush._http.get_json = original

    def test_baidu_html_block_page_behind_200_is_not_accepted(self):
        spec = indexpush.build_spec("baidu", ["https://a.com/1"],
                                    key="tok", site="www.a.com")
        out = self.execute_with_response(
            spec["request"], {"status": 200, "error": None, "json": None})
        self.assertFalse(out["accepted"])
        self.assertIn("unrecognized response", out["error"])

    def test_baidu_zero_success_count_is_not_accepted(self):
        spec = indexpush.build_spec("baidu", ["https://a.com/1"],
                                    key="tok", site="www.a.com")
        out = self.execute_with_response(
            spec["request"],
            {"status": 200, "error": None, "json": {"success": 0, "remain": 99}})
        self.assertFalse(out["accepted"])
        self.assertIn("success=0", out["error"])
        accepted = self.execute_with_response(
            spec["request"],
            {"status": 200, "error": None, "json": {"success": 1, "remain": 98}})
        self.assertTrue(accepted["accepted"])

    def test_indexnow_empty_200_stays_accepted(self):
        spec = indexpush.build_spec("indexnow", ["https://a.com/1"], key="abc123")
        out = self.execute_with_response(
            spec["request"], {"status": 200, "error": None, "json": None})
        self.assertTrue(out["accepted"])


class HnTests(unittest.TestCase):
    def test_numeric_filters_force_search_by_date_index(self):
        url, endpoint = hn.build_search_url("acme", tags="story")
        self.assertEqual(endpoint, "search")
        self.assertIn("/search?", url)
        self.assertIn("tags=story", url)
        filters = hn.build_numeric_filters(since_epoch=1750000000, min_points=50)
        self.assertEqual(filters, ["created_at_i>=1750000000", "points>=50"])
        url, endpoint = hn.build_search_url("acme", tags="(story,show_hn)",
                                            numeric_filters=filters)
        self.assertEqual(endpoint, "search_by_date")
        self.assertIn("/search_by_date?", url)
        self.assertIn("numericFilters=created_at_i%3E%3D1750000000%2Cpoints%3E%3D50", url)
        self.assertIn("tags=%28story%2Cshow_hn%29", url)
        # hitsPerPage clamped to [1, MAX_HITS]
        self.assertIn("hitsPerPage=100", hn.build_search_url("q", hits_per_page=500)[0])
        self.assertIn("hitsPerPage=1", hn.build_search_url("q", hits_per_page=0)[0])

    def test_rank_composes_list_position_and_comments_gt_points_fact(self):
        responses = {
            hn.build_firebase_url("showstories"): {"json": [111, 222, 333]},
            hn.build_firebase_url("item/222"): {"json": {
                "id": 222, "type": "story", "title": "Show HN: X",
                "score": 10, "descendants": 25, "by": "alice", "time": 0}},
        }
        original = hn._polite_get_json
        hn._polite_get_json = lambda url: responses[url]
        try:
            out = hn.rank(222, "showstories")
        finally:
            hn._polite_get_json = original
        self.assertEqual(out["rank"], 2)          # 1-based position
        self.assertEqual(out["list_size"], 3)
        self.assertEqual(out["points"], 10)
        self.assertEqual(out["descendants"], 25)
        self.assertTrue(out["comments_gt_points"])
        self.assertIsNone(hn.find_rank([111, 222, 333], 999))


class ProducthuntTests(unittest.TestCase):
    def test_day_window_defaults_to_last_completed_utc_day(self):
        today = _dt.date(2026, 7, 5)
        self.assertEqual(producthunt.day_window(today=today),
                         ("2026-07-04", "2026-07-04T00:00:00Z",
                          "2026-07-05T00:00:00Z"))
        self.assertEqual(producthunt.day_window("2026-06-30", today=today),
                         ("2026-06-30", "2026-06-30T00:00:00Z",
                          "2026-07-01T00:00:00Z"))
        with self.assertRaises(ValueError):
            producthunt.day_window("2026-07-05", today=today)  # in-progress day
        with self.assertRaises(ValueError):
            producthunt.day_window("2026-07-09", today=today)  # future day

    def test_build_query_caps_first_and_shapes_variables(self):
        q = producthunt.build_query("daily", posted_after="A",
                                    posted_before="B", first=500)
        self.assertEqual(q["variables"],
                         {"first": producthunt.MAX_POSTS, "after": "A",
                          "before": "B"})
        self.assertIn("order: VOTES", q["query"])
        post = producthunt.build_query("post", slug="my-app")
        self.assertEqual(post["variables"], {"slug": "my-app"})
        self.assertIn("createdAt", post["query"])
        topic = producthunt.build_query("topic", topic="ai", first=0)
        self.assertEqual(topic["variables"], {"topic": "ai", "first": 1})
        with self.assertRaises(ValueError):
            producthunt.build_query("nope")

    def test_classify_failure_rate_limit_auth_and_missing_token(self):
        code, err = producthunt.classify_failure(
            {"status": 429, "headers": {"X-Rate-Limit-Reset": "600"},
             "json": None})
        self.assertEqual((code, err["error"], err["reset_seconds"]),
                         (3, "rate_limited", "600"))
        # A rejected token (401/403) is a HARD error -> exit 2, not the transient
        # exit-3 rate-limit/skippable class (so smoke suites FAIL on a bad token).
        code, err = producthunt.classify_failure(
            {"status": 401, "headers": {}, "json": None})
        self.assertEqual((code, err["error"]), (2, "auth_failed"))
        self.assertIsNone(producthunt.classify_failure(
            {"status": 200, "headers": {},
             "json": {"data": {"posts": {"edges": []}}}}))
        # no --token, no env token, no client_credentials pair -> classified
        saved = {k: os.environ.pop(k, None) for k in
                 (producthunt.ENV_TOKEN, producthunt.ENV_CLIENT_ID,
                  producthunt.ENV_CLIENT_SECRET)}
        try:
            self.assertEqual(producthunt.resolve_token(),
                             ("", "no token configured"))
        finally:
            for k, v in saved.items():
                if v is not None:
                    os.environ[k] = v


class XquikTests(unittest.TestCase):
    def response(self, payload, status=200, headers=None, error=None):
        return {"status": status, "headers": headers or {}, "json": payload,
                "error": error}

    def test_build_url_locks_host_encodes_queries_and_bounds_users(self):
        url = xquik.build_url("search", params={"q": "brand & rival", "limit": 10})
        self.assertEqual(
            url,
            "https://xquik.com/api/v1/x/tweets/search?q=brand+%26+rival&limit=10",
        )
        self.assertEqual(
            xquik.build_url("posts", "@OpenAI", {"pageSize": 5}),
            "https://xquik.com/api/v1/x/users/OpenAI/tweets?pageSize=5",
        )
        with self.assertRaises(ValueError):
            xquik.build_url("profile", "bad/name")
        with self.assertRaises(ValueError):
            xquik.build_url("unknown")

    def test_query_and_page_bounds_are_deterministic(self):
        self.assertEqual(xquik.clamp_page_size(None), xquik.DEFAULT_PAGE_SIZE)
        self.assertEqual(xquik.clamp_page_size(0), 1)
        self.assertEqual(xquik.clamp_page_size(999), xquik.MAX_PAGE_SIZE)
        self.assertEqual(xquik.normalize_queries([" brand ", "brand", "rival"]),
                         ["brand", "rival"])
        with self.assertRaises(ValueError):
            xquik.normalize_queries(["q%d" % n for n in range(6)])
        with self.assertRaises(ValueError):
            xquik.validate_date("2026/08/22")

    def test_normalizers_accept_contract_and_legacy_field_shapes(self):
        profile = xquik.normalize_profile({
            "id": "1", "username": "acme", "followers": 9,
            "is_blue_verified": True, "created": "2026-01-01T00:00:00Z",
            "coverPicture": "https://example.com/cover.jpg",
        })
        self.assertEqual(profile["followers"], 9)
        self.assertTrue(profile["is_blue_verified"])
        self.assertEqual(profile["created_at"], "2026-01-01T00:00:00Z")
        self.assertEqual(
            profile["profile_banner_url"], "https://example.com/cover.jpg"
        )
        page = xquik.parse_page({
            "tweets": [{"id": "t1", "text": "fixture", "likeCount": 4,
                        "author": {"username": "a", "followersCount": 8,
                                   "profilePicture": "https://example.com/a.jpg"},
                        "media": [{"type": "photo",
                                   "mediaUrl": "https://example.com/photo.jpg",
                                   "url": "https://t.co/media"}]}],
            "has_next_page": True,
            "next_cursor": "opaque",
        })
        self.assertEqual(page["tweets"][0]["like_count"], 4)
        self.assertEqual(page["tweets"][0]["author"]["followers"], 8)
        self.assertEqual(
            page["tweets"][0]["author"]["profile_picture"],
            "https://example.com/a.jpg",
        )
        self.assertEqual(page["tweets"][0]["media"], [{
            "type": "photo",
            "media_url": "https://example.com/photo.jpg",
            "url": "https://t.co/media",
        }])
        self.assertTrue(page["has_more"])
        self.assertEqual(page["next_cursor"], "opaque")

    def test_failure_classes_preserve_retry_and_setup_detail(self):
        code, error = xquik.classify_failure(self.response(
            {"error": {"code": "rate_limit_exceeded", "message": "wait"}},
            status=429, headers={"Retry-After": "1"}))
        self.assertEqual((code, error["error"], error["retry_after"]),
                         (3, "rate_limited", "1"))
        code, error = xquik.classify_failure(self.response(
            {"error": "no_credits", "message": "top up"}, status=402))
        self.assertEqual((code, error["error"]), (3, "no_credits"))
        code, error = xquik.classify_failure(self.response(
            {"error": "unauthenticated"}, status=401))
        self.assertEqual((code, error["error"]), (2, "auth_failed"))
        self.assertIsNone(xquik.classify_failure(self.response({"tweets": []})))

    def test_listen_composes_queries_and_records_duplicate_membership(self):
        first = self.response({
            "tweets": [{"id": "shared", "text": "one"},
                       {"id": "brand-only", "text": "two"}],
            "has_more": True, "next_cursor": "brand-next",
        })
        second = self.response({
            "tweets": [{"id": "shared", "text": "one"},
                       {"id": "rival-only", "text": "three"}],
            "has_more": False, "next_cursor": "",
        })
        with mock.patch.object(xquik, "_call", side_effect=[first, second]) as call, \
             mock.patch.object(xquik.time, "sleep") as sleep:
            result, code = xquik.listen(
                "secret", ["brand", "rival"], limit=999, min_likes=2,
                from_user="acme",
            )
        self.assertEqual(code, 0)
        self.assertEqual(result["count"], 3)
        self.assertEqual(result["tweets"][0]["matched_queries"],
                         ["brand", "rival"])
        self.assertEqual(result["queries"][0]["next_cursor"], "brand-next")
        self.assertEqual(call.call_args_list[0].kwargs["params"]["limit"],
                         xquik.MAX_PAGE_SIZE)
        self.assertEqual(call.call_args_list[0].kwargs["params"]["fromUser"],
                         "acme")
        self.assertEqual(
            call.call_args_list[0].kwargs["params"]["minFaves"], 2
        )
        sleep.assert_called_once_with(xquik.MIN_INTERVAL)

        with self.assertRaises(ValueError):
            xquik.listen("secret", ["brand", "rival"], cursor="opaque")

    def test_listen_failure_preserves_partial_rows_and_count(self):
        first = self.response({
            "tweets": [{"id": "t1", "text": "fixture"}],
            "has_more": False,
        })
        second = self.response(
            {"error": {"code": "rate_limit_exceeded", "message": "wait"}},
            status=429,
            headers={"Retry-After": "2"},
        )
        with mock.patch.object(xquik, "_call", side_effect=[first, second]), \
             mock.patch.object(xquik.time, "sleep"):
            result, code = xquik.listen("secret", ["brand", "rival"])
        self.assertEqual(code, 3)
        self.assertTrue(result["partial"])
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["tweets"][0]["id"], "t1")
        self.assertEqual(result["retry_after"], "2")

    def test_creator_composes_profile_and_posts_with_cursor(self):
        profile = self.response({"id": "1", "username": "acme", "followers": 4})
        posts = self.response({
            "tweets": [{"id": "t1", "text": "fixture"}],
            "has_more": True, "next_cursor": "next",
        })
        with mock.patch.object(xquik, "_call", side_effect=[profile, posts]) as call, \
             mock.patch.object(xquik.time, "sleep"):
            result, code = xquik.creator("secret", "@acme", post_limit=3,
                                          include_replies=True, cursor="prior")
        self.assertEqual(code, 0)
        self.assertEqual(result["profile"]["username"], "acme")
        self.assertEqual(result["post_count"], 1)
        self.assertEqual(result["next_cursor"], "next")
        self.assertEqual(call.call_args_list[1].kwargs["params"], {
            "pageSize": 3, "includeReplies": "true", "cursor": "prior",
        })

    def test_mentions_normalizes_one_bounded_page(self):
        page = self.response({
            "tweets": [{"id": "m1", "text": "fixture"}],
            "has_more": True,
            "next_cursor": "next",
        })
        with mock.patch.object(xquik, "_call", return_value=page) as call:
            result, code = xquik.mentions(
                "secret", "@acme", limit=200, since="2026-08-01",
                until="2026-08-22", cursor="prior",
            )
        self.assertEqual(code, 0)
        self.assertEqual(result["user"], "acme")
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["next_cursor"], "next")
        self.assertEqual(call.call_args.kwargs["params"], {
            "pageSize": xquik.MAX_PAGE_SIZE,
            "sinceDate": "2026-08-01",
            "untilDate": "2026-08-22",
            "cursor": "prior",
        })


class AppstoreTests(unittest.TestCase):
    def test_lookup_batches_ids_and_flags_bad_ones(self):
        ids, bad = appstore.parse_ids(["310633997,284882215", "12345", "abc"])
        self.assertEqual(ids, ["310633997", "284882215", "12345", "abc"])
        self.assertEqual(bad, ["abc"])
        url = appstore.build_lookup_url(["310633997", "284882215"], "gb")
        self.assertIn("/lookup?", url)
        self.assertIn("id=310633997%2C284882215", url)  # comma-batched ids
        self.assertIn("country=gb", url)

    def test_charts_url_uses_new_marketingtools_host_and_documented_sizes(self):
        self.assertEqual(appstore.chart_size_for(10), 10)
        self.assertEqual(appstore.chart_size_for(11), 25)
        self.assertEqual(appstore.chart_size_for(999), 50)
        self.assertEqual(
            appstore.build_charts_url("us", "top-paid", appstore.chart_size_for(11)),
            "https://rss.marketingtools.apple.com/api/v2/us/apps/top-paid/25/apps.json")

    def test_search_url_locks_media_to_software_and_caps_limit(self):
        url = appstore.build_search_url("meditation app", "us", 500)
        self.assertIn("term=meditation+app", url)
        self.assertIn("country=us", url)
        self.assertIn("media=software", url)
        self.assertIn("limit=200", url)   # SEARCH_MAX cap
        self.assertIn("limit=1", appstore.build_search_url("x", "us", 0))


class BlueskyTests(unittest.TestCase):
    def test_build_xrpc_url_encodes_params_and_picks_base(self):
        url = bluesky.build_xrpc_url("app.bsky.actor.getProfile",
                                     {"actor": "bsky.app"})
        self.assertTrue(url.startswith(bluesky.PUBLIC_BASE + "/"))
        self.assertIn("app.bsky.actor.getProfile?", url)
        self.assertIn("actor=bsky.app", url)
        # search hits the authed base, not the public AppView
        authed = bluesky.build_xrpc_url("app.bsky.feed.searchPosts",
                                        {"q": "acme"}, base=bluesky.AUTH_BASE)
        self.assertTrue(authed.startswith(bluesky.AUTH_BASE + "/"))

    def test_clamp_limit_window_and_default(self):
        self.assertEqual(bluesky.clamp_limit(None), 25)
        self.assertEqual(bluesky.clamp_limit(0), 1)
        self.assertEqual(bluesky.clamp_limit(500), bluesky.MAX_LIMIT)

    def test_parse_since_and_bad_date(self):
        self.assertEqual(bluesky.parse_since("2026-06-01"),
                         "2026-06-01T00:00:00Z")
        with self.assertRaises(ValueError):
            bluesky.parse_since("2026/06/01")

    def test_resolve_credentials_over_supplied_mapping(self):
        ident, pw, err = bluesky.resolve_credentials(
            {"BSKY_IDENTIFIER": "me.bsky.social", "BSKY_APP_PASSWORD": "x-x"})
        self.assertEqual((ident, pw, err), ("me.bsky.social", "x-x", None))
        _, _, err = bluesky.resolve_credentials({"BSKY_IDENTIFIER": "me"})
        self.assertIn("BSKY_APP_PASSWORD", err)

    def test_parse_feed_marks_reposts(self):
        payload = {"feed": [
            {"post": {"uri": "at://1", "record": {"createdAt": "t1",
                      "text": "hi"}, "author": {"handle": "a"},
                      "likeCount": 3}},
            {"post": {"uri": "at://2", "record": {"createdAt": "t0"}},
             "reason": {"$type": "app.bsky.feed.defs#reasonRepost"}},
        ]}
        rows = bluesky.parse_feed(payload)
        self.assertEqual(rows[0]["likes"], 3)
        self.assertFalse(rows[0]["is_repost"])
        self.assertTrue(rows[1]["is_repost"])


class FediverseTests(unittest.TestCase):
    def test_normalize_instance_strips_scheme_and_path(self):
        self.assertEqual(fediverse.normalize_instance("https://mastodon.social/"),
                         "mastodon.social")
        self.assertEqual(fediverse.normalize_instance("HACHYDERM.IO/foo"),
                         "HACHYDERM.IO")

    def test_build_urls_cap_limits_and_encode(self):
        self.assertEqual(
            fediverse.build_trends_tags_url("mastodon.social", 999),
            "https://mastodon.social/api/v1/trends/tags?limit=%d"
            % fediverse.MAX_TRENDS)
        tag = fediverse.build_tag_url("mastodon.social", "#opensource", 5)
        self.assertIn("/api/v1/timelines/tag/opensource?", tag)
        self.assertIn("limit=5", tag)
        rss = fediverse.tag_rss_url("mastodon.social", "#opensource")
        self.assertEqual(rss, "https://mastodon.social/tags/opensource.rss")

    def test_build_lemmy_search_url_shape(self):
        url = fediverse.build_lemmy_search_url("lemmy.world", "self host",
                                               "TopMonth", 99)
        self.assertIn("type_=All", url)
        self.assertIn("sort=TopMonth", url)
        self.assertIn("limit=%d" % fediverse.LEMMY_MAX, url)  # capped

    def test_parse_trend_tag_totals_7day_uses(self):
        parsed = fediverse.parse_trend_tag({
            "name": "opensource", "url": "https://x/tags/opensource",
            "history": [{"day": "1751328000", "uses": "5", "accounts": "3"},
                        {"day": "1751241600", "uses": "2", "accounts": "1"}]})
        self.assertEqual(parsed["name"], "opensource")
        self.assertEqual(parsed["uses_7d"], 7)
        self.assertEqual(parsed["accounts_today"], 3)   # newest day first

    def test_strip_html_unwraps_paragraphs_and_entities(self):
        self.assertEqual(fediverse.strip_html("<p>a&amp;b<br>c</p>"), "a&b\nc")


class DiscourseTests(unittest.TestCase):
    def test_normalize_base_to_origin_no_trailing_slash(self):
        self.assertEqual(discourse.normalize_base("meta.discourse.org"),
                         "https://meta.discourse.org")
        self.assertEqual(
            discourse.normalize_base("https://meta.discourse.org/latest/"),
            "https://meta.discourse.org")

    def test_build_endpoint_urls(self):
        base = "https://meta.discourse.org"
        self.assertEqual(discourse.build_latest_url(base),
                         base + "/latest.json")
        self.assertEqual(discourse.build_topic_url(base, 42),
                         base + "/t/42.json")
        d = discourse.build_directory_url(base, period="monthly", limit=999)
        self.assertIn("/directory_items.json?", d)
        self.assertIn("period=monthly", d)
        self.assertIn("limit=%d" % discourse.DIRECTORY_MAX_API, d)  # capped

    def test_time_to_first_response_skips_op_self_replies(self):
        posts = [
            {"post_number": 1, "username": "op", "created_at": "2026-07-01T00:00:00Z"},
            {"post_number": 2, "username": "op", "created_at": "2026-07-01T00:05:00Z"},
            {"post_number": 3, "username": "other", "created_at": "2026-07-01T00:10:00Z"},
        ]
        self.assertEqual(discourse.time_to_first_response(posts), 600)
        # no reply by another user -> None (unanswered)
        self.assertIsNone(discourse.time_to_first_response(
            [{"post_number": 1, "username": "op",
              "created_at": "2026-07-01T00:00:00Z"}]))

    def test_parse_directory_tallies_trust_levels(self):
        payload = {"directory_items": [
            {"user": {"username": "a", "trust_level": 2}},
            {"user": {"username": "b", "trust_level": 2}},
            {"user": {"username": "c", "trust_level": 0}},
        ]}
        out = discourse.parse_directory(payload)
        self.assertEqual(out["rows_counted"], 3)
        self.assertEqual(out["trust_level_distribution"]["2_member"], 2)
        self.assertEqual(out["trust_level_distribution"]["0_new"], 1)


class ExperimentTests(unittest.TestCase):
    """Statistical correctness against known values (pure math, no network)."""

    def test_normal_helpers(self):
        self.assertAlmostEqual(experiment.norm_ppf(0.975), 1.959963985, places=6)
        self.assertAlmostEqual(experiment.norm_ppf(0.8), 0.841621234, places=6)
        self.assertAlmostEqual(experiment.norm_cdf(1.959963985), 0.975, places=6)
        for bad in (0.0, 1.0, -0.1, 1.1):
            with self.assertRaises(ValueError):
                experiment.norm_ppf(bad)

    def test_two_proportion_textbook(self):
        r = experiment.two_proportion(100, 1000, 130, 1000)
        self.assertAlmostEqual(r["z"], 2.1027, places=3)
        self.assertAlmostEqual(r["p_value"], 0.0355, places=3)
        self.assertTrue(r["statistically_significant"])
        self.assertTrue(r["practical_lift_clears_bar"])  # +30% clears 15% default
        self.assertNotIn("promote", r)
        self.assertAlmostEqual(r["relative_lift"], 0.30, places=6)
        self.assertTrue(r["effect_interval_excludes_zero"])
        self.assertEqual(r["provenance"]["outputs"], "calculated")

    def test_proportion_returns_separate_decision_inputs(self):
        # Statistical and practical flags remain distinct; no business verdict leaks out.
        r = experiment.two_proportion(100, 1000, 130, 1000, min_lift=0.40)
        self.assertTrue(r["statistically_significant"])
        self.assertFalse(r["practical_lift_clears_bar"])
        self.assertNotIn("promote", r)
        # equal rates -> not significant, p == 1.0
        r0 = experiment.two_proportion(100, 1000, 100, 1000)
        self.assertFalse(r0["statistically_significant"])
        self.assertAlmostEqual(r0["p_value"], 1.0, places=6)
        # bad input
        with self.assertRaises(ValueError):
            experiment.two_proportion(100, 50, 10, 100)   # conv > n

    def test_wilson_interval(self):
        lo, hi = experiment.wilson_interval(50, 100)
        self.assertAlmostEqual(lo, 0.404, places=2)
        self.assertAlmostEqual(hi, 0.596, places=2)
        self.assertEqual(experiment.wilson_interval(0, 0), (0.0, 0.0))

    def test_mann_whitney(self):
        sep = experiment.mann_whitney(list(range(1, 9)), list(range(9, 17)))
        self.assertEqual(sep["u"], 0.0)
        self.assertTrue(sep["p_value"] < 0.05)
        same = experiment.mann_whitney([1, 2, 3, 4, 5], [1, 2, 3, 4, 5])
        self.assertEqual(same["u"], 12.5)
        self.assertGreater(same["p_value"], 0.5)
        with self.assertRaises(ValueError):
            experiment.mann_whitney([], [1])

    def test_sample_size_roundtrip(self):
        ss = experiment.sample_size(0.10, 0.02)
        self.assertTrue(3000 < ss["n_per_variant"] < 4500)
        mde = experiment.min_detectable_effect(0.10, ss["n_per_variant"])
        self.assertAlmostEqual(mde["mde_absolute"], 0.02, places=3)

    def test_bootstrap_deterministic(self):
        a, b = [1, 2, 3, 4, 5], [3, 4, 5, 6, 7]
        r1 = experiment.bootstrap_diff(a, b, seed=0)
        r2 = experiment.bootstrap_diff(a, b, seed=0)
        self.assertEqual(r1["confidence_interval"], r2["confidence_interval"])
        self.assertAlmostEqual(r1["point_estimate"], 2.0, places=6)

    def test_edge_case_validation(self):
        # out-of-range alpha raises (was: crash / inverted CI / trivially significant)
        for bad in (0.0, 1.0, 1.5, -0.1):
            with self.assertRaises(ValueError):
                experiment.two_proportion(100, 1000, 130, 1000, alpha=bad)
            with self.assertRaises(ValueError):
                experiment.mann_whitney([1, 2, 3], [4, 5, 6], alpha=bad)
            with self.assertRaises(ValueError):
                experiment.bootstrap_diff([1, 2, 3], [4, 5, 6], alpha=bad)
            with self.assertRaises(ValueError):
                experiment.sample_size(0.10, 0.02, alpha=bad)
            with self.assertRaises(ValueError):
                experiment.min_detectable_effect(0.10, 4000, alpha=bad)
        with self.assertRaises(ValueError):        # B<1 was an IndexError on empty diffs
            experiment.bootstrap_diff([1, 2, 3], [4, 5, 6], B=0)
        with self.assertRaises(ValueError):
            experiment.two_proportion(100, 1000, 130, 1000, min_lift=-0.01)
        with self.assertRaises(ValueError):
            experiment.two_proportion(100, 1000, 130, 1000, alpha=float("nan"))
        with self.assertRaises(ValueError):
            experiment.mann_whitney([1, float("inf")], [2, 3])
        with self.assertRaises(ValueError):
            experiment.bootstrap_diff([1, 2], [3, float("nan")])
        for bad_power in (0.0, 1.0, 1.2, -0.1):
            with self.assertRaises(ValueError):
                experiment.sample_size(0.10, 0.02, power=bad_power)
            with self.assertRaises(ValueError):
                experiment.min_detectable_effect(0.10, 4000, power=bad_power)

    def test_zero_control_conversions(self):
        # Relative lift from a zero baseline is undefined; callers need an absolute bar.
        r = experiment.two_proportion(0, 1000, 50, 1000)
        self.assertTrue(r["statistically_significant"])
        self.assertIsNone(r["relative_lift"])
        self.assertIsNone(r["practical_lift_clears_bar"])
        self.assertEqual(r["direction"], "variant_higher")
        z = experiment.two_proportion(0, 1000, 0, 1000)
        self.assertFalse(z["statistically_significant"])
        self.assertFalse(z["practical_lift_clears_bar"])

    def test_degenerate_bootstrap_not_significant(self):
        # n=1 per arm: CI collapses to a point -> must NOT be read as significant
        boot = experiment.bootstrap_diff([5], [9])
        self.assertFalse(boot["reliable"])
        self.assertFalse(boot["interval_excludes_zero"])

    def test_norm_ppf_tail_branches(self):
        # Force Acklam's low/high-tail branches (p < 0.02425 / p > 0.97575), which use
        # a different coefficient set than the central branch the other tests hit.
        self.assertAlmostEqual(experiment.norm_ppf(0.001), -3.090232306, places=5)
        self.assertAlmostEqual(experiment.norm_ppf(0.999), 3.090232306, places=5)
        # symmetry across both tails
        self.assertAlmostEqual(experiment.norm_ppf(0.001), -experiment.norm_ppf(0.999), places=6)

    def test_mann_whitney_tie_correction(self):
        # A tie-heavy, asymmetric input where the tie correction actually moves the
        # answer — pins tie_term AND the continuity-correction sign together. A version
        # that drops the tie term (or flips the sign) fails this.
        r = experiment.mann_whitney([1, 1, 2, 3], [2, 3, 4, 4])
        self.assertAlmostEqual(r["z"], -1.6269, places=4)
        self.assertAlmostEqual(r["p_value"], 0.1038, places=4)
        # same shape with no ties gives a materially different (more significant) result
        r_notie = experiment.mann_whitney([1, 2, 3, 4], [5, 6, 7, 8])
        self.assertLess(r_notie["p_value"], r["p_value"])

    def test_bootstrap_median_path(self):
        # Exercises the stat='median' branch (agg=_median) through the resampling loop.
        b = experiment.bootstrap_diff([1, 2, 3, 4, 5], [10, 20, 30, 40, 50],
                                      stat="median", seed=0)
        self.assertEqual(b["statistic"], "median")
        self.assertAlmostEqual(b["point_estimate"], 27.0, places=6)  # median(b)-median(a)=30-3
        b2 = experiment.bootstrap_diff([1, 2, 3, 4, 5], [10, 20, 30, 40, 50],
                                       stat="median", seed=0)
        self.assertEqual(b["confidence_interval"], b2["confidence_interval"])

    def test_cli_main(self):
        # The user-facing CLI (main/build_parser/_floats/dispatch) — untested by the
        # direct-function cases above. Capture stdout so the run stays quiet.
        import io
        import contextlib

        def run(argv):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = experiment.main(argv)
            return rc, buf.getvalue()

        rc, out = run(["proportion", "--control", "100", "1000", "--variant", "130", "1000"])
        self.assertEqual(rc, 0)
        self.assertIn("statistically_significant", out)
        self.assertNotIn('"promote"', out)
        rc, out = run(["continuous", "--a", "1,2,3", "--b", "10,20,30",
                       "--stat", "median", "--seed", "0"])
        self.assertEqual(rc, 0)
        self.assertIn("mann_whitney", out)                # continuous combines MW + bootstrap
        rc, _ = run(["samplesize", "--baseline", "0.10", "--mde", "0.02"])
        self.assertEqual(rc, 0)
        # neither --mde nor --n -> documented exit-1 branch (message goes to stderr)
        with contextlib.redirect_stderr(io.StringIO()):
            rc, _ = run(["samplesize", "--baseline", "0.10"])
        self.assertEqual(rc, 1)
        # bad input -> ValueError caught -> exit 1
        with contextlib.redirect_stderr(io.StringIO()):
            rc, _ = run(["proportion", "--control", "100", "50", "--variant", "10", "100"])
        self.assertEqual(rc, 1)

    def test_effect_direction_is_factual(self):
        r = experiment.two_proportion(130, 1000, 100, 1000)
        self.assertTrue(r["statistically_significant"])
        self.assertLess(r["relative_lift"], 0)
        self.assertEqual(r["direction"], "variant_lower")
        self.assertFalse(r["practical_lift_clears_bar"])
        pos = experiment.two_proportion(100, 1000, 130, 1000, min_lift=0.5)
        self.assertTrue(pos["statistically_significant"])
        self.assertEqual(pos["direction"], "variant_higher")
        self.assertFalse(pos["practical_lift_clears_bar"])

    def test_output_notes_carry_caveats(self):
        # The overlapping-CI and no-peeking caveats must be in the emitted notes.
        prop = experiment.two_proportion(100, 1000, 130, 1000)
        self.assertIn("do NOT imply non-significance", prop["note"])
        self.assertIn("precommitted", prop["note"])
        cont = experiment.mann_whitney([1, 2, 3, 4], [5, 6, 7, 8])
        self.assertIn("peeking", cont["note"])


if __name__ == "__main__":
    unittest.main()
