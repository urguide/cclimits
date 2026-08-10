"""End-to-end tests for the non-blocking tmux status wrapper."""

import os
import subprocess
import time
from pathlib import Path


WRAPPER = Path(__file__).parents[1] / "bin" / "cclimits-tmux"


def _write_executable(path: Path, body: str) -> Path:
    path.write_text("#!/bin/sh\nset -eu\n" + body)
    path.chmod(0o755)
    return path


def _run_wrapper(tmp_path: Path, cclimits: Path, *, args: str, grok: Path | None = None) -> str:
    env = os.environ.copy()
    env.update({
        "TMPDIR": str(tmp_path),
        "CCLIMITS_BIN": str(cclimits),
        "CCLIMITS_TMUX_ARGS": args,
        "CCLIMITS_TMUX_TTL": "3600",
    })
    if grok:
        env["GROK_BIN"] = str(grok)
    return subprocess.run(
        ["bash", str(WRAPPER)], env=env, capture_output=True, text=True, check=True,
    ).stdout


def _wait_for_output(tmp_path: Path, cclimits: Path, *, args: str, expected: str,
                     grok: Path | None = None) -> None:
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        if _run_wrapper(tmp_path, cclimits, args=args, grok=grok).strip() == expected:
            return
        time.sleep(0.05)
    raise AssertionError(f"wrapper never produced {expected!r}")


def test_new_argument_view_keeps_last_known_display(tmp_path):
    """A new argument-keyed cache must not blank tmux while it warms up."""
    cclimits = _write_executable(tmp_path / "fake-cclimits", """
case "$*" in
  *--view-a*) printf 'Claude:10%%(2h)\\n' ;;
  *) sleep 1; printf 'Grok:20%%(3d)\\n' ;;
esac
""")

    _run_wrapper(tmp_path, cclimits, args="--view-a")
    _wait_for_output(tmp_path, cclimits, args="--view-a", expected="Claude:10%(2h)")

    # The first invocation for view B starts its slow refresh in the background
    # but immediately serves view A's stable display cache.
    assert _run_wrapper(tmp_path, cclimits, args="--view-b").strip() == "Claude:10%(2h)"
    _wait_for_output(tmp_path, cclimits, args="--view-b", expected="Grok:20%(3d)")


def test_expired_grok_is_refreshed_by_official_models_command(tmp_path):
    """The wrapper delegates rotation/write-back to `grok models`, then retries."""
    marker = tmp_path / "refreshed"
    cclimits = _write_executable(tmp_path / "fake-cclimits", f"""
if [ -f {marker!s} ]; then
  printf 'Grok:55%%(7d)\\n'
else
  printf 'Grok:expired\\n'
fi
""")
    grok = _write_executable(tmp_path / "fake-grok", f"""
[ "$1" = models ]
: > {marker!s}
""")

    _run_wrapper(tmp_path, cclimits, args="--grok", grok=grok)
    _wait_for_output(
        tmp_path, cclimits, args="--grok", grok=grok, expected="Grok:55%(7d)",
    )
    assert marker.exists()


def test_plain_text_failure_does_not_replace_good_cache(tmp_path):
    """Compact `expired` output receives the same protection as emoji errors."""
    state = tmp_path / "fail"
    cclimits = _write_executable(tmp_path / "fake-cclimits", f"""
if [ -f {state!s} ]; then
  printf 'Grok:expired\\n'
else
  printf 'Grok:55%%(7d)\\n'
fi
""")

    _run_wrapper(tmp_path, cclimits, args="--grok")
    _wait_for_output(tmp_path, cclimits, args="--grok", expected="Grok:55%(7d)")
    state.touch()

    # Force another lease cycle without deleting the good data/display cache.
    for lease in tmp_path.glob("*.lease"):
        lease.unlink()
    _run_wrapper(tmp_path, cclimits, args="--grok")
    time.sleep(0.2)
    assert _run_wrapper(tmp_path, cclimits, args="--grok").strip() == "Grok:55%(7d)"


def test_watch_mode_keeps_emitting_complete_lines(tmp_path):
    """Long-running tmux mode must never alternate a valid line with blank output."""
    cclimits = _write_executable(
        tmp_path / "fake-cclimits", "printf 'Claude:10%%(2h)_Grok:20%%(3d)\\n'\n",
    )
    env = os.environ.copy()
    env.update({
        "TMPDIR": str(tmp_path),
        "CCLIMITS_BIN": str(cclimits),
        "CCLIMITS_TMUX_ARGS": "--test",
        "CCLIMITS_TMUX_TTL": "3600",
        "CCLIMITS_TMUX_WATCH_INTERVAL": "0.05",
    })
    proc = subprocess.Popen(
        ["bash", str(WRAPPER), "--watch"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        deadline = time.monotonic() + 5
        lines = []
        while len(lines) < 4 and time.monotonic() < deadline:
            line = proc.stdout.readline().strip()
            if line:
                lines.append(line)
        assert lines == ["Claude:10%(2h)_Grok:20%(3d)"] * 4
    finally:
        proc.terminate()
        proc.wait(timeout=5)
