import subprocess
from functools import singledispatchmethod
import adb_tool_py as adb_tool
import adb_tool_py.command as command


class AdbCommand:
    """
    A class to execute ADB commands on a specified Android device.
    """
    device: adb_tool.AdbDevice = None

    def __init__(self, adb: str = "adb", device: adb_tool.AdbDevice = None):
        """
        Initializes the AdbCommand class.

        :param adb: Path to the ADB executable, defaults to "adb".
        :param device: An instance of AdbDevice to specify the target device, defaults to None.
        """
        self.adb = adb
        self.set_device(device)

    def set_device(self, device: adb_tool.AdbDevice) -> 'AdbCommand':
        """
        Sets the target device for ADB commands.

        :param device: An instance of AdbDevice.
        :return: The current instance of AdbCommand.
        """
        self.device = device
        return self

    def _base_cmd(self) -> list:
        """
        Constructs the base ADB command with the target device.

        :return: A list representing the base ADB command.
        """
        if self.device is None or self.device.serial is None:
            return [self.adb]
        else:
            return [self.adb, '-s', self.device.serial]

    @singledispatchmethod
    def query(self, cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) -> subprocess.CompletedProcess:
        """
        Executes an ADB command and waits for it to complete.

        :param cmd: The command to execute (str or list).
        :param stdout: Standard output pipe, defaults to subprocess.PIPE.
        :param stderr: Standard error pipe, defaults to subprocess.PIPE.
        :return: The completed process.
        """
        raise NotImplementedError("Unsupported type")

    @query.register
    def _(self, cmd: str, stdout=subprocess.PIPE, stderr=subprocess.PIPE) -> subprocess.CompletedProcess:
        """
        Executes an ADB command given as a string.

        :param cmd: The command to execute (str).
        :param stdout: Standard output pipe, defaults to subprocess.PIPE.
        :param stderr: Standard error pipe, defaults to subprocess.PIPE.
        :return: The completed process.
        """
        return self.query(cmd.split(' '), stdout, stderr)

    @query.register
    def _(self, cmd: list, stdout=subprocess.PIPE, stderr=subprocess.PIPE) -> subprocess.CompletedProcess:
        """
        Executes an ADB command given as a list of arguments.

        :param cmd: The command to execute (list).
        :param stdout: Standard output pipe, defaults to subprocess.PIPE.
        :param stderr: Standard error pipe, defaults to subprocess.PIPE.
        :return: The completed process.
        """
        ret = command.command(*self._base_cmd(), *cmd, stdout=stdout, stderr=stderr)
        if ret.returncode != 0:
            raise RuntimeError(f"Error: {ret.stderr.decode()}")
        return ret

    @singledispatchmethod
    def query_async(self, cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) -> subprocess.Popen:
        """
        Executes an ADB command asynchronously.

        :param cmd: The command to execute (str or list).
        :param stdout: Standard output pipe, defaults to subprocess.PIPE.
        :param stderr: Standard error pipe, defaults to subprocess.PIPE.
        :return: The process object.
        """
        raise NotImplementedError("Unsupported type")

    @query_async.register
    def _(self, cmd: str, stdout=subprocess.PIPE, stderr=subprocess.PIPE) -> subprocess.Popen:
        """
        Executes an ADB command asynchronously given as a string.

        :param cmd: The command to execute (str).
        :param stdout: Standard output pipe, defaults to subprocess.PIPE.
        :param stderr: Standard error pipe, defaults to subprocess.PIPE.
        :return: The process object.
        """
        return self.query_async(cmd.split(' '), stdout, stderr)

    @query_async.register
    def _(self, cmd: list, stdout=subprocess.PIPE, stderr=subprocess.PIPE) -> subprocess.Popen:
        """
        Executes an ADB command asynchronously given as a list of arguments.

        :param cmd: The command to execute (list).
        :param stdout: Standard output pipe, defaults to subprocess.PIPE.
        :param stderr: Standard error pipe, defaults to subprocess.PIPE.
        :return: The process object.
        """
        return command.command_async(*self._base_cmd(), *cmd, stdout=stdout, stderr=stderr)
