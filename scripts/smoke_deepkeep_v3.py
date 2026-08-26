from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Literal

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from deepkeep_openwebui_filter import _decision_from_response  # noqa: E402


async def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test DeepKeep v3 moderation endpoints.")
    parser.add_argument("--phase", choices=["pre", "post", "both"], default="both")
    parser.add_argument("--content", default="Hello from the DeepKeep Open WebUI smoke test.")
    parser.add_argument("--title", default="DeepKeep Open WebUI smoke test")
    parser.add_argument("--chat", default="smoke-test")
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args()

    api_key = os.environ.get("DEEPKEEP_API_KEY", "").strip()
    base_url = os.environ.get("DEEPKEEP_BASE_URL", "").strip().rstrip("/")
    pre_model = os.environ.get("DEEPKEEP_PRE_MODEL", "").strip()
    post_model = os.environ.get("DEEPKEEP_POST_MODEL", "").strip()

    if not api_key or not base_url:
        print("DEEPKEEP_API_KEY and DEEPKEEP_BASE_URL are required.", file=sys.stderr)
        return 2
    if args.phase in {"pre", "both"} and not pre_model:
        print("DEEPKEEP_PRE_MODEL is required for pre moderation.", file=sys.stderr)
        return 2
    if args.phase in {"post", "both"} and not post_model:
        print("DEEPKEEP_POST_MODEL is required for post moderation.", file=sys.stderr)
        return 2

    async with httpx.AsyncClient(timeout=args.timeout) as client:
        if args.phase in {"pre", "both"}:
            await run_check(
                client=client,
                base_url=base_url,
                api_key=api_key,
                phase="pre",
                payload={"model": pre_model, "input": args.content, "title": args.title, "chat": args.chat},
            )
        if args.phase in {"post", "both"}:
            await run_check(
                client=client,
                base_url=base_url,
                api_key=api_key,
                phase="post",
                payload={"model": post_model, "output": args.content, "title": args.title, "chat": args.chat},
            )

    return 0


async def run_check(
    *,
    client: httpx.AsyncClient,
    base_url: str,
    api_key: str,
    phase: Literal["pre", "post"],
    payload: dict[str, Any],
) -> None:
    response = await client.post(
        f"{base_url}/api/v3/openai/moderations/{phase}",
        headers={"X-API-Key": api_key, "Accept": "application/json"},
        json=payload,
    )
    response.raise_for_status()
    result = response.json()
    decision = _decision_from_response(result)
    print(
        json.dumps(
            {
                "phase": phase,
                "action": decision.action,
                "reason": decision.reason,
                "modified_content": decision.modified_content,
                "unsupported_action": decision.unsupported_action,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
