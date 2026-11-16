"""Detects which language toolchains are usable on the current machine.

Tests that compile or run generated code need real compilers (GNU g++,
javac, rustc, dmd, nim, mcs+mono). These helpers let both the pytest
collection hook (tests/conftest.py) and unittest bodies skip such tests
cleanly instead of failing with "command not found" or missing-header
errors on machines that lack the toolchain.

Detection is probe-based where it matters: PATH existence alone is not
enough (e.g. macOS ships javac/java stubs that fail at runtime, and
Apple clang provides g++ without <bits/stdc++.h>).
"""
import os
import shutil
import subprocess
import tempfile
from typing import Callable, Dict, List, Optional

_PROBE_CACHE: Dict[str, bool] = {}


def _run_quietly(argv: List[str], cwd: str) -> bool:
    try:
        return subprocess.run(
            argv,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=cwd,
        ).returncode == 0
    except OSError:
        return False


def _write_source(tmpdir: str, name: str, content: str) -> str:
    path = os.path.join(tmpdir, name)
    with open(path, "w") as f:
        f.write(content)
    return path


def _probe(name: str, probe_body: Callable[[str], bool]) -> bool:
    """Caches the result of probe_body(tmpdir) -> bool under `name`."""
    if name not in _PROBE_CACHE:
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                _PROBE_CACHE[name] = probe_body(tmpdir)
        except OSError:
            _PROBE_CACHE[name] = False
    return _PROBE_CACHE[name]


def _has_commands(*commands: str) -> bool:
    return all(shutil.which(cmd) is not None for cmd in commands)


def _probe_cpp(tmpdir: str) -> bool:
    src = _write_source(
        tmpdir, "probe.cpp", "#include <bits/stdc++.h>\nint main() { return 0; }\n")
    return _run_quietly(["g++", src, "-o", "probe"], tmpdir)


def _probe_java(tmpdir: str) -> bool:
    # A public class must live in a file of the same name for javac.
    _write_source(
        tmpdir, "Probe.java",
        "public class Probe { public static void main(String[] a) {} }\n")
    return _run_quietly(["javac", "Probe.java"], tmpdir) \
        and _run_quietly(["java", "-cp", ".", "Probe"], tmpdir)


def _probe_rust(tmpdir: str) -> bool:
    _write_source(tmpdir, "probe.rs", "fn main() {}\n")
    return _run_quietly(["rustc", "probe.rs", "-o", "probe"], tmpdir)


def _probe_dlang(tmpdir: str) -> bool:
    _write_source(tmpdir, "probe.d", "void main() {}\n")
    return _run_quietly(["dmd", "probe.d", "-of=probe"], tmpdir)


def _probe_csharp(tmpdir: str) -> bool:
    _write_source(
        tmpdir, "probe.cs", "public class Probe { static void Main() {} }\n")
    return _run_quietly(["mcs", "probe.cs"], tmpdir) \
        and _run_quietly(["mono", "probe.exe"], tmpdir)


def _probe_nim(_tmpdir: str) -> bool:
    # A full `nim c` compile is too heavy for a probe; a version check is
    # enough to detect absent/broken installs.
    return _run_quietly(["nim", "--version"], ".")


def _probe_python(_tmpdir: str) -> bool:
    return _run_quietly(["python3", "-c", "pass"], ".")


# lang.name -> (probe, human-readable requirement used in skip reasons)
TOOLCHAIN_PROBES: Dict[str, Callable[[str], bool]] = {
    "cpp": _probe_cpp,
    "java": _probe_java,
    "rust": _probe_rust,
    "python": _probe_python,
    "d": _probe_dlang,
    "nim": _probe_nim,
    "cs": _probe_csharp,
}

TOOLCHAIN_DESCRIPTIONS: Dict[str, str] = {
    "cpp": "GNU g++ supporting <bits/stdc++.h>",
    "java": "javac and java",
    "rust": "rustc",
    "python": "python3",
    "d": "dmd",
    "nim": "nim",
    "cs": "mcs and mono",
}

# pytest marker name -> lang.name (must stay in sync with pyproject.toml markers)
MARKER_TO_LANG: Dict[str, str] = {
    "requires_cpp": "cpp",
    "requires_java": "java",
    "requires_rust": "rust",
    "requires_dlang": "d",
    "requires_nim": "nim",
    "requires_csharp": "cs",
}


def toolchain_available(lang_name: str) -> bool:
    probe = TOOLCHAIN_PROBES.get(lang_name)
    if probe is None:
        return True
    return _probe(lang_name, probe)


def skip_reason_for(lang_name: str) -> str:
    return "requires {} on PATH".format(
        TOOLCHAIN_DESCRIPTIONS.get(lang_name, lang_name))
