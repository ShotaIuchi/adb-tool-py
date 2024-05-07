import subprocess


def command(*args, stdout=subprocess.PIPE, stderr=subprocess.PIPE) -> subprocess.CompletedProcess:
    cmd = list(args)
    print(f'sync:{cmd}')
    ret = subprocess.run(cmd, stdout=stdout, stderr=stderr, text=True)
    return ret


def command_async(*args, stdout=subprocess.PIPE, stderr=subprocess.PIPE) -> subprocess.Popen:
    cmd = list(args)
    print(f'async:{cmd}')
    return subprocess.Popen(cmd, stdout=stdout, stderr=stderr, text=True)
