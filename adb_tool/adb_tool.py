import io
import subprocess
import tempfile
import adb_tool.adb_command as adb_command
import adb_tool.adb_view_tree as adb_view_tree
import adb_tool.ui_node as ui_node


class AdbWrap:
    def __init__(self, adb: adb_command.AdbCommand = adb_command.AdbCommand()):
        self.adb = adb
        self.adbv = adb_view_tree.AdbViewTree(adb)

    def adb(self, cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) -> str:
        return self.adb.query(cmd, stdout, stderr)

    def adb_async(self, cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) -> subprocess.Popen:
        return self.adb.query_async(cmd, stdout, stderr)

    def logcat(self, output_file=None, cmd: str = '') -> tuple[subprocess.Popen, io.TextIOWrapper]:
        if output_file is None:
            output_file = tempfile.NamedTemporaryFile(delete=False)
        return self.adb_async(['logcat', *(cmd.split(' '))], stdout=output_file), output_file

    def logcat_clear(self, cmd: str = '') -> str:
        return self.adb(['logcat', '-c', *(cmd.split(' '))])

    def logcat_dump(self, cmd: str = '') -> str:
        return self.adb(['logcat', '-d', *(cmd.split(' '))])

    def capture(self) -> None:
        self.adbv.capture()

    def content_tree(self) -> adb_view_tree.ui_node.UINode:
        return self.adbv.content_tree

    def find_text(self, text: str, index: int = 0, root_node: ui_node.UINode = None, is_capture: bool = False) -> adb_view_tree.ui_node.UINode:
        return self.adbv.find_text(text, index, root_node, is_capture)

    def find_resource_id(self, resource_id: str, index: int = 0, root_node: ui_node.UINode = None, is_capture: bool = False) -> adb_view_tree.ui_node.UINode:
        return self.adbv.find_resource_id(resource_id, index, root_node, is_capture)

    def check_text(self, text: str, index: int = 0, root_node: ui_node.UINode = None, is_capture: bool = False) -> bool:
        return self.adbv.check_text(text, index, root_node, is_capture)

    def check_resource_id(self, resource_id: str, index: int = 0, root_node: ui_node.UINode = None, is_capture: bool = False) -> bool:
        return self.adbv.check_resource_id(resource_id, index, root_node, is_capture)

    def touch_text(self, text: str, index: int = 0, root_node: ui_node.UINode = None, is_capture: bool = False) -> bool:
        return self.adbv.touch_text(text, index, root_node, is_capture)

    def touch_resource_id(self, resource_id: str, index: int = 0, root_node: ui_node.UINode = None, is_capture: bool = False) -> bool:
        return self.adbv.touch_resource_id(resource_id, index, root_node, is_capture)
