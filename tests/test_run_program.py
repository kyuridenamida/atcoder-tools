import os
import sys
import tempfile
import unittest

from atcodertools.executils.run_program import (
    ExecStatus,
    _resolve_exec_command,
    run_program,
)


class TestResolveExecCommand(unittest.TestCase):

    def test_plain_command_is_untouched(self):
        self.assertEqual(
            ["python3", "main.py"],
            _resolve_exec_command("python3 main.py"))

    def test_relative_path_is_resolved_to_absolute(self):
        resolved = _resolve_exec_command("./main")
        self.assertEqual([os.path.abspath("./main")], resolved)

    def test_nested_relative_path_is_resolved(self):
        resolved = _resolve_exec_command(os.path.join("abc001", "A", "main"))
        self.assertEqual(
            [os.path.abspath(os.path.join("abc001", "A", "main"))],
            resolved)

    def test_extra_arguments_are_kept(self):
        resolved = _resolve_exec_command("./main --verbose")
        self.assertEqual(
            [os.path.abspath("./main"), "--verbose"], resolved)


class TestRunProgram(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def _write(self, name, content):
        path = os.path.join(self.temp_dir, name)
        with open(path, "w") as f:
            f.write(content)
        return path

    def test_script_is_run_via_interpreter(self):
        # A .py file without the executable bit must still run: it is
        # invoked through the interpreter instead of being exec'ed
        # directly (which fails on Windows and for some script files).
        script = self._write(
            "main.py", "import sys\nsys.stdout.write(sys.stdin.read())")
        in_file = self._write("in_1.txt", "hello\n")

        res = run_program(script, in_file, 1.0)

        self.assertEqual(ExecStatus.NORMAL, res.status)
        self.assertEqual("hello\n", res.output)

    def test_relative_exec_path_with_working_dir(self):
        # Regression test for the failure where a relative --dir made
        # the executable unresolvable because subprocess.run looks up a
        # relative executable path relative to cwd.
        script = self._write(
            "main.py", "import sys\nsys.stdout.write(sys.stdin.read())")
        in_file = self._write("in_1.txt", "hi\n")

        basename = os.path.basename(self.temp_dir)
        parent = os.path.dirname(self.temp_dir)
        saved = os.getcwd()
        try:
            os.chdir(parent)
            res = run_program(
                os.path.join(basename, "main.py"),
                os.path.join(basename, "in_1.txt"),
                1.0,
                current_working_dir=basename,
            )
        finally:
            os.chdir(saved)

        self.assertEqual(ExecStatus.NORMAL, res.status)
        self.assertEqual("hi\n", res.output)


if __name__ == '__main__':
    unittest.main()
