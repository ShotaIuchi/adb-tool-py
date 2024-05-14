import io
import os
import subprocess
import tempfile
import adb_tool_py as adb_tool
import adb_tool_py.ui_node as ui_node


class LogcatContext:
    def __init__(self, subprocess: subprocess.Popen, file: io.TextIOWrapper, is_delete: bool = True):
        self.subprocess = subprocess
        self.file = file
        self.is_delete = is_delete

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def open(self, mode='r'):
        return open(self.file.name, mode)

    def close(self):
        self.file.close()
        if self.is_delete:
            os.remove(self.file.name)
        self.subprocess.terminate()
        self.subprocess.wait()


class AdbTool:
    def __init__(self, adb_command: adb_tool.AdbCommand = None, adb: str = "adb", serial: str = None):
        self.adb = adb_command
        if adb_command is None:
            self.adb = adb_tool.AdbCommand(adb, adb_tool.AdbDevice(serial))
        self.avt = adb_tool.AdbViewTree(self.adb)

    def query(self, cmd: str, stdout=subprocess.PIPE, stderr=subprocess.PIPE) -> subprocess.Popen:
        return self.adb.query(cmd, stdout, stderr)

    def query_async(self, cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) -> subprocess.Popen:
        return self.adb.query_async(cmd, stdout, stderr)

    def logcat(self, output_file=None, cmd: str = '') -> LogcatContext:
        is_delete = False
        if output_file is None:
            output_file = tempfile.NamedTemporaryFile(delete=False)
            is_delete = True
        sp = self.query_async(
            ['logcat', *(cmd.split(' '))], stdout=output_file)
        return LogcatContext(sp, output_file, is_delete)

    def logcat_clear(self, cmd: str = '') -> str:
        return self.query(['logcat', '-c', *(cmd.split(' '))])

    def logcat_dump(self, cmd: str = '') -> str:
        return self.query(['logcat', '-d', *(cmd.split(' '))])

    def capture(self) -> None:
        self.avt.capture()

    def content_tree(self) -> ui_node.UINode:
        return self.avt.content_tree

    def find_text(self, text: str, index: int = 0, root_node: ui_node.UINode = None, is_capture: bool = False) -> ui_node.UINode:
        return self.avt.find_text(text, index, root_node, is_capture)

    def find_resource_id(self, resource_id: str, index: int = 0, root_node: ui_node.UINode = None, is_capture: bool = False) -> ui_node.UINode:
        return self.avt.find_resource_id(resource_id, index, root_node, is_capture)

    def check_text(self, text: str, index: int = 0, root_node: ui_node.UINode = None, is_capture: bool = False) -> bool:
        return self.avt.check_text(text, index, root_node, is_capture)

    def check_resource_id(self, resource_id: str, index: int = 0, root_node: ui_node.UINode = None, is_capture: bool = False) -> bool:
        return self.avt.check_resource_id(resource_id, index, root_node, is_capture)

    def touch_text(self, text: str, index: int = 0, root_node: ui_node.UINode = None, is_capture: bool = False) -> bool:
        return self.avt.touch_text(text, index, root_node, is_capture)

    def touch_resource_id(self, resource_id: str, index: int = 0, root_node: ui_node.UINode = None, is_capture: bool = False) -> bool:
        return self.avt.touch_resource_id(resource_id, index, root_node, is_capture)
