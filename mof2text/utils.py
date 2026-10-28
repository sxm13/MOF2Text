import contextlib
import os
import sys


def _flush_all():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.flush()
        except Exception:
            pass
    # Julia (CrystalNets) buffers its own stdout/stderr
    if "juliacall" in sys.modules:
        try:
            sys.modules["juliacall"].Main.seval("flush(stdout); flush(stderr)")
        except Exception:
            pass


@contextlib.contextmanager
def suppress_output(log_file=None, enabled=True):
    """Hide everything written to stdout/stderr inside the block, including
    output from C extensions, subprocesses (MOFid, Zeo++) and Julia
    (CrystalNets) -- not just Python's print().

    log_file: if given, the hidden output is appended to this file instead
              of being discarded.
    enabled:  set False to show the output (verbose mode).
    """
    if not enabled:
        yield
        return

    _flush_all()
    target = open(log_file, "a") if log_file else open(os.devnull, "w")
    saved = []
    try:
        # OS level: covers subprocesses, C code and Julia
        for fd in (1, 2):
            try:
                saved.append((fd, os.dup(fd)))
                os.dup2(target.fileno(), fd)
            except OSError:
                pass
        # Python level: covers Jupyter/IDE consoles where sys.stdout is not fd 1
        with contextlib.redirect_stdout(target), contextlib.redirect_stderr(target):
            yield
    finally:
        _flush_all()
        for fd, dup in saved:
            os.dup2(dup, fd)
            os.close(dup)
        target.close()
