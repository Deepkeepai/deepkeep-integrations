"""Read-only GHCR checks for the Agentgateway release."""

import argparse
import base64
import json
import os
import re
import ssl
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, HTTPSHandler, Request, build_opener


REGISTRY = "https://ghcr.io"
NAME = "deepkeepai/agentgateway-deepkeep-webhook"
ACCEPT = ", ".join((
    "application/vnd.oci.image.index.v1+json",
    "application/vnd.oci.image.manifest.v1+json",
    "application/vnd.docker.distribution.manifest.list.v2+json",
    "application/vnd.docker.distribution.manifest.v2+json",
    "application/vnd.docker.distribution.manifest.v1+json",
    "application/vnd.docker.distribution.manifest.v1+prettyjws",
))
DIGEST = r"sha256:[0-9a-f]{64}"


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def request(opener, url, headers, method="GET"):
    try:
        try:
            response = opener.open(Request(url, headers=headers, method=method), timeout=15)
        except HTTPError as error:
            response = error
        with response:
            status = response.code
            body = response.read(65537) if method == "GET" and status == 200 else b""
            if len(body) > 65536:
                raise ValueError("Registry response rejected")
            return status, response.headers, body
    except (OSError, URLError, ValueError):
        raise ValueError("Registry request failed") from None


def check_release(version, expected_digest=None):
    if re.fullmatch(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", version) is None:
        raise ValueError("Invalid release version")
    if expected_digest is not None and re.fullmatch(DIGEST, expected_digest) is None:
        raise ValueError("Invalid expected digest")
    actor = os.environ.get("GITHUB_ACTOR", "")
    credential = os.environ.get("GITHUB_TOKEN", "")
    if not actor or ":" in actor or not credential:
        raise ValueError("Missing or invalid credentials")
    opener = build_opener(HTTPSHandler(context=ssl.create_default_context()), NoRedirect())
    basic = base64.b64encode(f"{actor}:{credential}".encode("utf-8")).decode("ascii")
    query = urlencode({"service": "ghcr.io", "scope": f"repository:{NAME}:pull"})
    status, _, body = request(opener, f"{REGISTRY}/token?{query}", {"Authorization": f"Basic {basic}"})
    if status != 200:
        raise ValueError("Registry authentication failed")
    try:
        payload = json.loads(body)
        tokens = [payload[key] for key in ("token", "access_token") if key in payload]
        if not tokens or any(
            not isinstance(token, str) or not token or any(ord(c) < 33 or ord(c) > 126 for c in token)
            for token in tokens
        ) or len(set(tokens)) != 1:
            raise ValueError
        token = tokens[0]
    except (ValueError, TypeError, KeyError):
        raise ValueError("Registry token rejected") from None
    headers = {"Authorization": f"Bearer {token}", "Accept": ACCEPT}
    digests = []
    for tag in (version, "latest"):
        status, response_headers, _ = request(
            opener, f"{REGISTRY}/v2/{NAME}/manifests/{tag}", headers, method="HEAD"
        )
        if expected_digest is None and tag == version:
            if status != 404:
                raise ValueError("Version must be unused")
            continue
        digest = response_headers.get("Docker-Content-Digest", "")
        if status != 200 or re.fullmatch(DIGEST, digest) is None:
            raise ValueError("Manifest check failed")
        if expected_digest is not None and digest != expected_digest:
            raise ValueError("Published digest mismatch")
        digests.append(digest)
    return digests[-1]


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError("Invalid arguments")


def main():
    parser = Parser(description=__doc__)
    parser.add_argument("version")
    parser.add_argument("--expected-digest")
    try:
        args = parser.parse_args()
        digest = check_release(args.version, args.expected_digest)
    except Exception:
        print("Container release check failed", file=sys.stderr)
        return 1
    key = "published_digest" if args.expected_digest is not None else "previous_digest"
    print(f"{key}={digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
