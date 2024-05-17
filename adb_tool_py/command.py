import subprocess


def command(*args, stdout=subprocess.PIPE, stderr=subprocess.PIPE) -> subprocess.CompletedProcess:
    """
    Executes a command synchronously and waits for it to complete.

    :param args: The command and its arguments to execute.
    :param stdout: Standard output pipe, defaults to subprocess.PIPE.
    :param stderr: Standard error pipe, defaults to subprocess.PIPE.
    :return: The completed process.
    """
    cmd = list(args)
    print(f'sync: {cmd}')
    # Execute the command and wait for it to complete
    ret = subprocess.run(cmd, stdout=stdout, stderr=stderr, text=True)
    return ret


def command_async(*args, stdout=subprocess.PIPE, stderr=subprocess.PIPE) -> subprocess.Popen:
    """
    Executes a command asynchronously.

    :param args: The command and its arguments to execute.
    :param stdout: Standard output pipe, defaults to subprocess.PIPE.
    :param stderr: Standard error pipe, defaults to subprocess.PIPE.
    :return: The process object.
    """
    cmd = list(args)
    print(f'async: {cmd}')
    # Execute the command asynchronously
    return subprocess.Popen(cmd, stdout=stdout, stderr=stderr, text=True)
