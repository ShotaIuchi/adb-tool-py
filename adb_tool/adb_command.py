import subprocess
from functools import singledispatchmethod
import adb_tool.adb_device as adb_device
import adb_tool.command as command


class AdbCommand:
    device: adb_device.AdbDevice = None

    def __init__(self, adb: str = "adb"):
        self.adb = adb

    def _base_cmd(self) -> list:
        if self.device is None:
            return [self.adb]
        else:
            return [self.adb, '-s', self.device.serial]

    def set_device(self, device: adb_device.AdbDevice):
        self.device = device

    @singledispatchmethod
    def query(self, cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) -> subprocess.CompletedProcess:
        raise NotImplementedError("Unsupported type")

    @query.register
    def _(self, cmd: str, stdout=subprocess.PIPE, stderr=subprocess.PIPE) -> subprocess.CompletedProcess:
        return self.query(cmd.split(' '), stdout, stderr)

    @query.register
    def _(self, cmd: list, stdout=subprocess.PIPE, stderr=subprocess.PIPE) -> subprocess.CompletedProcess:
        ret = command.command(*self._base_cmd(), *cmd,
                              stdout=stdout, stderr=stderr)
        if ret.returncode != 0:
            raise Exception(f"Error: {ret.stderr}")
        return ret

    @singledispatchmethod
    def query_async(self, cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) -> subprocess.Popen:
        raise NotImplementedError("Unsupported type")

    @query_async.register
    def _(self, cmd: str, stdout=subprocess.PIPE, stderr=subprocess.PIPE) -> subprocess.Popen:
        return self.query_async(cmd.split(' '), stdout, stderr)

    @query_async.register
    def _(self, cmd: list, stdout=subprocess.PIPE, stderr=subprocess.PIPE) -> subprocess.Popen:
        return command.command_async(*self._base_cmd(), *cmd, stdout=stdout, stderr=stderr)
