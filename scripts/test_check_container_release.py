import base64
from contextlib import redirect_stderr, redirect_stdout
from email.message import Message
import io
import json
import ssl
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlsplit

import check_container_release as release


DIGEST = "sha256:" + "a" * 64
OTHER_DIGEST = "sha256:" + "b" * 64


class Response(io.BytesIO):
    def __init__(self, status=200, body=b"", digest=None):
        super().__init__(body)
        self.code = status
        self.headers = Message()
        if digest is not None:
            self.headers["Docker-Content-Digest"] = digest


class ContainerReleaseTests(unittest.TestCase):
    def setUp(self):
        env = patch.dict("os.environ", {"GITHUB_ACTOR": "actor", "GITHUB_TOKEN": "private-secret"}, clear=True)
        env.start()
        self.addCleanup(env.stop)
        opener = patch.object(release, "build_opener")
        self.factory = opener.start()
        self.addCleanup(opener.stop)
        self.opener = self.factory.return_value

    def responses(self, *manifests, body=b'{"token":"registry-secret"}'):
        self.opener.open.side_effect = [Response(body=body), *manifests]

    def test_preflight_and_pinned_requests(self):
        self.responses(Response(404), Response(digest=DIGEST))
        self.assertEqual(release.check_release("1.2.3"), DIGEST)
        calls = self.opener.open.call_args_list
        self.assertEqual(len(calls), 3)
        token_request = calls[0].args[0]
        url = urlsplit(token_request.full_url)
        self.assertEqual((url.scheme, url.netloc, url.path), ("https", "ghcr.io", "/token"))
        self.assertEqual(parse_qs(url.query), {
            "service": ["ghcr.io"], "scope": [f"repository:{release.NAME}:pull"]
        })
        basic = base64.b64encode(b"actor:private-secret").decode()
        self.assertEqual(token_request.get_header("Authorization"), f"Basic {basic}")
        self.assertEqual(token_request.get_method(), "GET")
        for call, tag in zip(calls[1:], ("1.2.3", "latest")):
            request = call.args[0]
            self.assertEqual(request.get_method(), "HEAD")
            self.assertEqual(request.full_url, f"https://ghcr.io/v2/{release.NAME}/manifests/{tag}")
            self.assertEqual(request.get_header("Accept"), release.ACCEPT)
            self.assertEqual(request.get_header("Authorization"), "Bearer registry-secret")
        for call in calls:
            self.assertEqual(call.kwargs, {"timeout": 15})
        handlers = self.factory.call_args.args
        self.assertTrue(any(isinstance(handler, release.NoRedirect) for handler in handlers))
        https = next(handler for handler in handlers if isinstance(handler, release.HTTPSHandler))
        self.assertTrue(https._context.check_hostname)
        self.assertEqual(https._context.verify_mode, ssl.CERT_REQUIRED)

    def test_postflight(self):
        self.responses(Response(digest=DIGEST), Response(digest=DIGEST))
        self.assertEqual(release.check_release("0.1.0", DIGEST), DIGEST)

    def test_existing_version_rejected_even_if_matching(self):
        self.responses(Response(digest=DIGEST))
        with self.assertRaises(ValueError):
            release.check_release("1.2.3")
        self.assertEqual(self.opener.open.call_count, 2)

    def test_unexpected_manifest_statuses(self):
        for status in (201, 204, 301, 302, 303, 307, 308, 400, 401, 403, 429, 500, 503):
            for position in ("version", "latest"):
                with self.subTest(status=status, position=position):
                    manifests = [Response(status)] if position == "version" else [Response(404), Response(status)]
                    self.responses(*manifests)
                    with self.assertRaises(ValueError):
                        release.check_release("1.2.3")

    def test_missing_latest_rejected(self):
        self.responses(Response(404), Response(404))
        with self.assertRaises(ValueError):
            release.check_release("1.2.3")

    def test_invalid_manifest_digests(self):
        for digest in (None, "", "sha256:abc", "sha512:" + "a" * 64, "sha256:" + "A" * 64, DIGEST + "\n"):
            with self.subTest(digest=digest):
                self.responses(Response(404), Response(digest=digest))
                with self.assertRaises(ValueError):
                    release.check_release("1.2.3")

    def test_postflight_requires_both_matches(self):
        for manifests in (
            (Response(digest=OTHER_DIGEST), Response(digest=DIGEST)),
            (Response(digest=DIGEST), Response(digest=OTHER_DIGEST)),
            (Response(404), Response(digest=DIGEST)),
            (Response(digest=DIGEST), Response(404)),
        ):
            self.responses(*manifests)
            with self.assertRaises(ValueError):
                release.check_release("1.2.3", DIGEST)

    def test_invalid_versions_before_network(self):
        for version in ("1.2", "v1.2.3", "1.2.3-rc1", "01.2.3", "1.2.3\n", "../latest", "1.2.3;echo", "\u0661.2.3"):
            with self.subTest(version=version), self.assertRaises(ValueError):
                release.check_release(version)
        self.opener.open.assert_not_called()

    def test_invalid_expected_digest_before_network(self):
        for digest in ("", "abc", "sha256:123", DIGEST + "\n"):
            with self.subTest(digest=digest), self.assertRaises(ValueError):
                release.check_release("1.2.3", digest)
        self.opener.open.assert_not_called()

    def test_missing_credentials(self):
        for actor, token in (("", "token"), ("actor", ""), ("bad:actor", "token")):
            with patch.dict("os.environ", {"GITHUB_ACTOR": actor, "GITHUB_TOKEN": token}):
                with self.assertRaises(ValueError):
                    release.check_release("1.2.3")
        self.opener.open.assert_not_called()

    def test_token_fields(self):
        for payload in ({"access_token": "registry-secret"}, {"token": "registry-secret", "access_token": "registry-secret"}):
            self.responses(Response(404), Response(digest=DIGEST), body=json.dumps(payload).encode())
            self.assertEqual(release.check_release("1.2.3"), DIGEST)

    def test_invalid_token_responses(self):
        for body in (b"not json", b"{}", b"null", b"[]", b'{"token":null}', b'{"token":42}',
                     b'{"token":""}', b'{"token":"bad\\nheader"}', b'{"token":"a","access_token":"b"}',
                     b" " * 65537):
            with self.subTest(body_length=len(body)):
                self.responses(body=body)
                with self.assertRaises(ValueError):
                    release.check_release("1.2.3")

    def test_token_status_failures(self):
        for status in (201, 301, 302, 307, 308, 401, 403, 404, 500, 503):
            self.opener.open.side_effect = [Response(status)]
            with self.subTest(status=status), self.assertRaises(ValueError):
                release.check_release("1.2.3")

    def test_network_failures(self):
        for error in (URLError("private-secret"), TimeoutError("private-secret"), ssl.SSLError("private-secret")):
            self.opener.open.side_effect = error
            with self.assertRaisesRegex(ValueError, "^Registry request failed$"):
                release.check_release("1.2.3")

    def test_http_error_404_is_unused(self):
        missing = HTTPError("https://ghcr.io/", 404, "secret", Message(), io.BytesIO(b"secret body"))
        self.responses(missing, Response(digest=DIGEST))
        self.assertEqual(release.check_release("1.2.3"), DIGEST)

    def test_redirect_blocked_without_followup(self):
        self.assertIsNone(release.NoRedirect().redirect_request(None, None, 302, "", {}, "https://evil.example"))
        for position in (0, 1, 2):
            responses = [Response(body=b'{"token":"secret"}'), Response(404), Response(digest=DIGEST)]
            headers = Message()
            headers["Location"] = "https://evil.example/upload-secret"
            responses[position] = HTTPError("https://ghcr.io/", 302, "secret", headers, io.BytesIO())
            self.opener.open.side_effect = responses
            self.opener.open.reset_mock()
            with self.assertRaises(ValueError):
                release.check_release("1.2.3")
            self.assertEqual(self.opener.open.call_count, position + 1)

    def test_token_body_read_is_bounded(self):
        response = Response(body=b"x" * 65537)
        with patch.object(response, "read", wraps=response.read) as read:
            self.opener.open.side_effect = [response]
            with self.assertRaises(ValueError):
                release.check_release("1.2.3")
            read.assert_called_once_with(65537)

    def test_cli_outputs_only_digest(self):
        for expected in (None, DIGEST):
            manifests = [Response(404), Response(digest=DIGEST)] if expected is None else [Response(digest=DIGEST), Response(digest=DIGEST)]
            self.responses(*manifests)
            argv = ["check_container_release.py", "1.2.3"]
            if expected is not None:
                argv.extend(["--expected-digest", expected])
            stdout, stderr = io.StringIO(), io.StringIO()
            with patch("sys.argv", argv), redirect_stdout(stdout), redirect_stderr(stderr):
                self.assertEqual(release.main(), 0)
            key = "previous_digest" if expected is None else "published_digest"
            self.assertEqual(stdout.getvalue(), f"{key}={DIGEST}\n")
            self.assertEqual(stderr.getvalue(), "")

    def test_cli_errors_are_generic(self):
        for argv in (["check", "1.2.3"], ["check", "1.2.3", "--private-secret"]):
            self.opener.open.side_effect = URLError("private-secret body upload-url")
            stdout, stderr = io.StringIO(), io.StringIO()
            with patch("sys.argv", argv), redirect_stdout(stdout), redirect_stderr(stderr):
                self.assertEqual(release.main(), 1)
            self.assertEqual(stdout.getvalue(), "")
            self.assertEqual(stderr.getvalue(), "Container release check failed\n")


if __name__ == "__main__":
    unittest.main()
