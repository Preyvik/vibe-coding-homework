"""PR Review Committee — supervisor multi-agent review using Claude Agent SDK."""

import argparse
import asyncio
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv
from claude_agent_sdk import query, ClaudeAgentOptions

from agents import (
    SECURITY_AUDITOR,
    PERFORMANCE_REVIEWER,
    STYLE_CHECKER,
    SUPERVISOR_SYSTEM_PROMPT,
)

SUPERVISOR_MODEL = "claude-opus-4-7"
HERE = Path(__file__).parent
OUTPUT_FILE = HERE / "review-output.md"
DEFAULT_DIFF = HERE / "sample.diff"


def load_diff(args) -> str:
    if args.staged:
        result = subprocess.run(
            ["git", "diff", "--staged"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    path = Path(args.diff_path) if args.diff_path else DEFAULT_DIFF
    return path.read_text(encoding="utf-8")


async def run_committee(diff_text: str) -> str:
    options = ClaudeAgentOptions(
        system_prompt=SUPERVISOR_SYSTEM_PROMPT,
        model=SUPERVISOR_MODEL,
        agents={
            "security-auditor": SECURITY_AUDITOR,
            "performance-reviewer": PERFORMANCE_REVIEWER,
            "style-checker": STYLE_CHECKER,
        },
        allowed_tools=["Agent", "Task", "Read", "Grep", "Glob"],
        permission_mode="bypassPermissions",
    )

    user_message = (
        "Here is the git diff to review. Dispatch all three specialist "
        "sub-agents (security-auditor, performance-reviewer, style-checker) "
        "IN PARALLEL — invoke them in a single batch, do not wait for one to "
        "finish before invoking the next. Then aggregate their reports into "
        "the final PR Review.\n\n"
        f"```diff\n{diff_text}\n```"
    )

    streaming_text: list[str] = []
    final_result: str | None = None

    async for message in query(prompt=user_message, options=options):
        result = getattr(message, "result", None)
        if isinstance(result, str) and result.strip():
            final_result = result
            continue
        content = getattr(message, "content", None)
        if content:
            for block in content:
                text = getattr(block, "text", None)
                if isinstance(text, str):
                    streaming_text.append(text)

    return (final_result or "\n".join(streaming_text)).strip()


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    load_dotenv()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY not set. Copy .env.example to .env and fill it in.")

    parser = argparse.ArgumentParser(
        description="PR Review Committee — supervisor multi-agent review."
    )
    parser.add_argument(
        "diff_path",
        nargs="?",
        default=None,
        help="Path to a .diff file (default: sample.diff in this folder)",
    )
    parser.add_argument(
        "--staged",
        action="store_true",
        help="Use `git diff --staged` from current repo instead of a file",
    )
    args = parser.parse_args()

    diff_text = load_diff(args)
    if not diff_text.strip():
        sys.exit("Diff is empty. Stage some changes or pass a non-empty diff file.")

    print("Spouštím PR Review Committee (3 sub-agenti paralelně)...\n")
    final = asyncio.run(run_committee(diff_text))

    print(final)
    OUTPUT_FILE.write_text(final + "\n", encoding="utf-8")
    print(f"\n---\nVýstup uložen do: {OUTPUT_FILE.name}")


if __name__ == "__main__":
    main()
