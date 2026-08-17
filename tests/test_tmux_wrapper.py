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


def _run_wrapper(tmp_path: Path, cclimits: Path, *, args: str, grok: Path | None = None,
                 **extra: str) -> str:
    env = os.environ.copy()
    env.update({
        "TMPDIR": str(tmp_path),
        "CCLIMITS_BIN": str(cclimits),
        "CCLIMITS_TMUX_ARGS": args,
        "CCLIMITS_TMUX_TTL": "3600",
    })
    if grok:
        env["GROK_BIN"] = str(grok)
    env.update(extra)
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


def test_expired_grok_is_refreshed_when_labeled_by_icon(tmp_path):
    """--icons renames the Grok label, and the refresh trigger must follow it.

    Matching only the word `Grok` would leave icon users stuck on `expired`
    until the next manual `grok` run, with no visible sign that the recovery
    path had silently stopped firing.
    """
    grok_icon = "\ueb72"  # cod-twitter, cclimits' --icons label for Grok
    marker = tmp_path / "refreshed"
    cclimits = _write_executable(tmp_path / "fake-cclimits", f"""
if [ -f {marker!s} ]; then
  printf '{grok_icon}:55%%(7d)\\n'
else
  printf '{grok_icon}:expired\\n'
fi
""")
    grok = _write_executable(tmp_path / "fake-grok", f"""
[ "$1" = models ]
: > {marker!s}
""")

    _run_wrapper(tmp_path, cclimits, args="--grok", grok=grok)
    _wait_for_output(
        tmp_path, cclimits, args="--grok", grok=grok,
        expected=f"{grok_icon}:55%(7d)",
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


def test_missing_credentials_do_not_block_refresh(tmp_path):
    """`no key` is a stable config state, not a transient failure to protect against.

    Treating it as a failure would reject every refresh forever, freezing the
    percentages of the providers that *are* working.
    """
    state = tmp_path / "second"
    cclimits = _write_executable(tmp_path / "fake-cclimits", f"""
if [ -f {state!s} ]; then
  printf 'Claude:22%%(2h)_Grok:no key\\n'
else
  printf 'Claude:11%%(2h)_Grok:no key\\n'
fi
""")

    _run_wrapper(tmp_path, cclimits, args="--all")
    _wait_for_output(
        tmp_path, cclimits, args="--all", expected="Claude:11%(2h)_Grok:no key",
    )
    state.touch()

    # Force another lease cycle without deleting the existing cache.
    for lease in tmp_path.glob("*.lease"):
        lease.unlink()
    _run_wrapper(tmp_path, cclimits, args="--all")
    _wait_for_output(
        tmp_path, cclimits, args="--all", expected="Claude:22%(2h)_Grok:no key",
    )


def _read_watch_lines(tmp_path: Path, cclimits: Path, count: int, **extra: str) -> list[str]:
    env = os.environ.copy()
    env.update({
        "TMPDIR": str(tmp_path),
        "CCLIMITS_BIN": str(cclimits),
        "CCLIMITS_TMUX_ARGS": "--test",
        "CCLIMITS_TMUX_TTL": "3600",
        "CCLIMITS_TMUX_WATCH_INTERVAL": "0.05",
    })
    env.update(extra)
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
        while len(lines) < count and time.monotonic() < deadline:
            lines.append(proc.stdout.readline().rstrip("\n"))
        return lines
    finally:
        proc.terminate()
        proc.wait(timeout=5)


def test_watch_mode_keeps_emitting_complete_lines(tmp_path):
    """Long-running tmux mode must never alternate a valid line with blank output."""
    cclimits = _write_executable(
        tmp_path / "fake-cclimits", "printf 'Claude:10%%(2h)_Grok:20%%(3d)\\n'\n",
    )
    expected = "Claude:10%(2h)_Grok:20%(3d)"
    lines = _read_watch_lines(
        tmp_path, cclimits, 6, CCLIMITS_TMUX_PLACEHOLDER="WARMING",
    )

    # Every emission is a complete line, and the cold-cache placeholder only
    # ever precedes real data — never interleaves with it.
    assert "" not in lines
    assert set(lines) <= {"WARMING", expected}
    assert lines[-1] == expected
    assert lines == sorted(lines, key=lambda line: line != "WARMING")


def test_watch_mode_emits_placeholder_on_cold_cache(tmp_path):
    """A blank first line makes tmux render its own `<'...' not ready>` marker."""
    cclimits = _write_executable(
        tmp_path / "fake-cclimits", "sleep 3\nprintf 'Claude:10%%(2h)\\n'\n",
    )
    assert _read_watch_lines(tmp_path, cclimits, 2) == ["cclimits...", "cclimits..."]


def test_watch_mode_placeholder_can_be_disabled(tmp_path):
    """An explicitly empty placeholder must not fall back to the default."""
    cclimits = _write_executable(
        tmp_path / "fake-cclimits", "sleep 3\nprintf 'Claude:10%%(2h)\\n'\n",
    )
    lines = _read_watch_lines(
        tmp_path, cclimits, 2, CCLIMITS_TMUX_PLACEHOLDER="",
    )
    assert lines == ["", ""]


# A Varnish/Fastly error page, as actually observed overwriting an installed
# wrapper when `curl -o` (no `-f`) hit a 503.
CDN_ERROR_PAGE = (
    '<?xml version="1.0" encoding="utf-8"?>\n'
    "<html><head><title>503 between bytes timeout</title></head>\n"
    "<body><h1>Error 503 between bytes timeout</h1></body></html>\n"
)


def _watch_lines_after_corruption(wrapper: Path, tmp_path: Path, count: int,
                                  **extra: str) -> list[str]:
    """Corrupt the wrapper *after* its watch loop is already running.

    The loop must be parsed into memory first, mirroring the real incident: a
    long-lived watcher keeps ticking after the file underneath it is replaced,
    and only the `"$0"` child invocations fail.
    """
    env = os.environ.copy()
    env.update({
        "TMPDIR": str(tmp_path),
        "CCLIMITS_BIN": str(tmp_path / "fake-cclimits"),
        "CCLIMITS_TMUX_ARGS": "--test",
        "CCLIMITS_TMUX_TTL": "3600",
        "CCLIMITS_TMUX_WATCH_INTERVAL": "0.05",
    })
    env.update(extra)
    proc = subprocess.Popen(
        ["bash", str(wrapper), "--watch"],
        env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    try:
        # One healthy tick proves the loop is live before we break the file.
        assert proc.stdout.readline().rstrip("\n") != ""
        wrapper.write_text(CDN_ERROR_PAGE)

        # Ticks already in flight may still carry good output; collect until the
        # corruption takes effect, then verify it is sustained.
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            first = proc.stdout.readline().rstrip("\n")
            if first not in ("Claude:10%(2h)", ""):
                break
        else:
            raise AssertionError("wrapper never reported a broken invocation")

        lines = [first]
        while len(lines) < count and time.monotonic() < deadline:
            lines.append(proc.stdout.readline().rstrip("\n"))
        return lines
    finally:
        proc.terminate()
        proc.wait(timeout=5)


def _install_wrapper_copy(tmp_path: Path) -> Path:
    _write_executable(tmp_path / "fake-cclimits", "printf 'Claude:10%%(2h)\\n'\n")
    wrapper = tmp_path / "cclimits-tmux"
    wrapper.write_text(WRAPPER.read_text())
    wrapper.chmod(0o755)
    return wrapper


def test_watch_mode_reports_a_broken_self_invocation_distinctly(tmp_path):
    """A corrupted wrapper must not masquerade as a merely-cold cache.

    Observed in the wild: `curl -o` (no `-f`) stored a CDN 503 HTML page as the
    installed wrapper. The already-running watch loop was parsed in memory so it
    kept ticking, but every `"$0"` child invocation failed. Output was empty, so
    the loop printed the cold-cache placeholder forever and the status line gave
    no hint that the script itself was gone.
    """
    wrapper = _install_wrapper_copy(tmp_path)
    lines = _watch_lines_after_corruption(
        wrapper, tmp_path, 2,
        CCLIMITS_TMUX_PLACEHOLDER="WARMING", CCLIMITS_TMUX_ERROR="BROKEN",
    )
    assert lines == ["BROKEN", "BROKEN"]


def test_watch_mode_error_line_defaults_and_differs_from_placeholder(tmp_path):
    """The default error marker must be distinguishable from the placeholder."""
    wrapper = _install_wrapper_copy(tmp_path)
    lines = _watch_lines_after_corruption(wrapper, tmp_path, 2)
    assert lines == ["cclimits!", "cclimits!"]
    assert "cclimits..." not in lines


# CCLIMITS_TMUX_SEP — replace --compact's `_` with a display separator, so the
# status line can use the same coloured bar as the pane/window dividers.

TMUX_BAR = "#[fg=#ff8800]\u2503#[fg=cyan]"


def test_separator_is_substituted_when_serving(tmp_path):
    cclimits = _write_executable(
        tmp_path / "fake-cclimits", "printf 'Claude:10%%(2h)_Grok:20%%(3d)\\n'\n",
    )
    _run_wrapper(tmp_path, cclimits, args="--all")
    _wait_for_output(tmp_path, cclimits, args="--all", expected="Claude:10%(2h)_Grok:20%(3d)")

    out = _run_wrapper(tmp_path, cclimits, args="--all", CCLIMITS_TMUX_SEP=TMUX_BAR)
    assert out.strip() == f"Claude:10%(2h){TMUX_BAR}Grok:20%(3d)"


def test_separator_is_not_written_to_the_cache(tmp_path):
    """Substituting on write would defeat the transient-failure grep below and
    would delay a separator change until the refresh TTL expired."""
    cclimits = _write_executable(
        tmp_path / "fake-cclimits", "printf 'Claude:10%%(2h)_Grok:20%%(3d)\\n'\n",
    )
    _run_wrapper(tmp_path, cclimits, args="--all", CCLIMITS_TMUX_SEP=TMUX_BAR)
    _wait_for_output(
        tmp_path, cclimits, args="--all", expected="Claude:10%(2h)_Grok:20%(3d)",
    )

    for cache in tmp_path.glob("*.cache"):
        assert cache.read_text().strip() == "Claude:10%(2h)_Grok:20%(3d)"

    # And with no separator configured the served line is byte-identical to the
    # cache, i.e. the feature is strictly opt-in.
    assert _run_wrapper(tmp_path, cclimits, args="--all").strip() == \
        "Claude:10%(2h)_Grok:20%(3d)"


def test_separator_does_not_break_transient_failure_protection(tmp_path):
    """The last-good grep matches the raw `:expired(_|$)` form.  A separator
    written into the cache would make it unmatchable, so an outage would start
    overwriting good readings the moment a user configured one."""
    state = tmp_path / "fail"
    cclimits = _write_executable(tmp_path / "fake-cclimits", f"""
if [ -f {state!s} ]; then
  printf 'Claude:10%%(2h)_Grok:expired\\n'
else
  printf 'Claude:10%%(2h)_Grok:55%%(7d)\\n'
fi
""")
    good = "Claude:10%(2h)_Grok:55%(7d)"
    _run_wrapper(tmp_path, cclimits, args="--all", CCLIMITS_TMUX_SEP=TMUX_BAR)
    _wait_for_output(tmp_path, cclimits, args="--all", expected=good)
    state.touch()

    for lease in tmp_path.glob("*.lease"):
        lease.unlink()
    _run_wrapper(tmp_path, cclimits, args="--all", CCLIMITS_TMUX_SEP=TMUX_BAR)
    time.sleep(0.2)
    assert _run_wrapper(tmp_path, cclimits, args="--all").strip() == good


def test_separator_is_inserted_literally(tmp_path):
    """tmux style strings contain `#`, and users reach for `|` bars; `&` and `\\`
    are sed metacharacters.  All must survive verbatim."""
    cclimits = _write_executable(
        tmp_path / "fake-cclimits", "printf 'A:1%%_B:2%%\\n'\n",
    )
    sep = r"#[fg=red]|&\x#[default]"
    _run_wrapper(tmp_path, cclimits, args="--all")
    _wait_for_output(tmp_path, cclimits, args="--all", expected="A:1%_B:2%")

    out = _run_wrapper(tmp_path, cclimits, args="--all", CCLIMITS_TMUX_SEP=sep)
    assert out.strip() == f"A:1%{sep}B:2%"


def test_separator_applies_in_watch_mode(tmp_path):
    """Watch mode is the documented tmux entry point, so the substitution has to
    reach it — it re-invokes this script rather than sharing its serve path."""
    cclimits = _write_executable(
        tmp_path / "fake-cclimits", "printf 'Claude:10%%(2h)_Grok:20%%(3d)\\n'\n",
    )
    expected = f"Claude:10%(2h){TMUX_BAR}Grok:20%(3d)"
    lines = _read_watch_lines(
        tmp_path, cclimits, 6,
        CCLIMITS_TMUX_PLACEHOLDER="WARMING",
        CCLIMITS_TMUX_SEP=TMUX_BAR,
    )
    assert set(lines) <= {"WARMING", expected}
    assert lines[-1] == expected
