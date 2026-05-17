import pathlib
import shutil
import tempfile

from pwncli.commands import cmd_template


CURDIR = pathlib.Path(__file__).parent
SRCDIR = CURDIR / "../sources"


class _Ctx:
    def vlog(self, *_args, **_kwargs):
        return None


def test_generate_pwn_exp_uu64_escape(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = pathlib.Path(tmpdir)
        shutil.copyfile(SRCDIR / "pwn", tmpdir / "pwn")
        shutil.copyfile(SRCDIR / "libc-2.31.so", tmpdir / "libc-2.31.so")

        monkeypatch.setattr(cmd_template, "which", lambda _name: None)

        cmd_template.generate_pwn_exp(_Ctx(), str(tmpdir))

        data = (tmpdir / "exp_pwn.py").read_bytes()
        assert b"\x00" not in data
        assert b'uu64 = lambda recvlen: u64(recvlen.ljust(8, b"\\\\x00"))' in data
