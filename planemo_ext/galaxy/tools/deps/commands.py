import os
import subprocess
import sys as _sys


def redirecting_io(sys=_sys):
    assert sys is not None
    # We are redirecting standard out and standard error.
    return not hasattr(sys.stdout, "fileno")


def redirect_aware_commmunicate(p, sys=_sys):
    assert sys is not None
    out, err = p.communicate()
    if redirecting_io(sys=sys):
        if out:
            sys.stdout.write(out)
            out = None
        if err:
            sys.stderr.write(err)
            err = None
    return out, err


def shell(cmds, env=None, **kwds):
    sys = kwds.get("sys", _sys)
    assert sys is not None
    p = shell_process(cmds, env, **kwds)
    if redirecting_io(sys=sys):
        redirect_aware_commmunicate(p, sys=sys)
        exit = p.returncode
        return exit
    else:
        return p.wait()


def shell_process(cmds, env=None, **kwds):
    sys = kwds.get("sys", _sys)
    popen_kwds = dict(
        shell=True,
    )
    if kwds.get("stdout", None) is None and redirecting_io(sys=sys):
        popen_kwds["stdout"] = subprocess.PIPE
    if kwds.get("stderr", None) is None and redirecting_io(sys=sys):
        popen_kwds["stderr"] = subprocess.PIPE

    popen_kwds.update(**kwds)
    if env:
        new_env = os.environ.copy()
        new_env.update(env)
        popen_kwds["env"] = new_env
    p = subprocess.Popen(cmds, **popen_kwds)
    return p


def execute(cmds):
    return __wait(cmds, shell=False)


def which(file):
    # http://stackoverflow.com/questions/5226958/which-equivalent-function-in-python
    for path in os.environ["PATH"].split(":"):
        if os.path.exists(path + "/" + file):
                return path + "/" + file

    return None


def __wait(cmds, **popen_kwds):
    p = subprocess.Popen(cmds, **popen_kwds)
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        raise CommandLineException(" ".join(cmds), stdout, stderr)
    return stdout


class CommandLineException(Exception):

    def __init__(self, command, stdout, stderr):
        self.command = command
        self.stdout = stdout
        self.stderr = stderr
        self.message = ("Failed to execute command-line %s, stderr was:\n"
                        "-------->>begin stderr<<--------\n"
                        "%s\n"
                        "-------->>end stderr<<--------\n"
                        "-------->>begin stdout<<--------\n"
                        "%s\n"
                        "-------->>end stdout<<--------\n"
                        ) % (command, stderr, stdout)

    def __str__(self):
        return self.message
