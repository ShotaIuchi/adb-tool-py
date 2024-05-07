import chardet
import os
import tempfile
import xml.etree.ElementTree as ET
import adb_tool.adb_command as adb_command
import adb_tool.ui_node as ui_node


DEVICE_FILE_PATH = '/sdcard/window_dump.xml'


def _parse_uiautomator_tree(content: str) -> ui_node.UINode:
    root_element = ET.fromstring(content)
    root_node = ui_node.UINode(root_element)
    _build_tree(root_element, root_node)
    return root_node


def _build_tree(element: str, current_node: ui_node.UINode) -> None:
    for child_element in element:
        if child_element.tag == 'node':
            child_node = ui_node.UINode(child_element, parent=current_node)
            current_node.add_child(child_node)
            _build_tree(child_element, child_node)


class AdbViewTree:
    content: str = None
    content_tree: ui_node.UINode = None

    def __init__(self, adb: adb_command.AdbCommand = adb_command.AdbCommand()):
        self.adb = adb

    def capture(self) -> None:
        # capture
        ret = self.adb.query(f'shell uiautomator dump {DEVICE_FILE_PATH}')
        if ret.returncode != 0:
            raise Exception(f"Error: {ret.stderr}")

        # get file
        with tempfile.NamedTemporaryFile(delete=False) as file:
            ret = self.adb.query(f'pull {DEVICE_FILE_PATH} {file.name}')
            if ret.returncode != 0:
                os.remove(file.name)
                raise Exception(f"Error: {ret.stderr}")

        # get encoding
        with open(file.name, 'rb') as file:
            raw_data = file.read()
            encoding = chardet.detect(raw_data)['encoding']

        # read content
        with open(file.name, 'r', encoding=encoding) as file:
            content = file.read()

        os.remove(file.name)
        self.content = content
        self.content_tree = _parse_uiautomator_tree(content)

    def find_text(self, text: str, index: int = 0, root_node: ui_node.UINode = None, is_capture: bool = False) -> ui_node.UINode:
        return self.find_node('text', text, index, root_node, is_capture)

    def check_text(self, text: str, index: int = 0, root_node: ui_node.UINode = None, is_capture: bool = False) -> bool:
        node = self.find_text(text, index, root_node, is_capture)
        return node is not None

    def touch_text(self, text: str, index: int = 0, root_node: ui_node.UINode = None, is_capture: bool = False) -> bool:
        node = self.find_text(text, index, root_node, is_capture)
        if node is None:
            return False
        ret = self.adb.query(
            f'shell input tap {node.center[0]} {node.center[1]}')
        return ret.returncode == 0

    def find_resource_id(self, resource_id: str, index: int = 0, root_node: ui_node.UINode = None, is_capture: bool = False) -> ui_node.UINode:
        return self.find_node('resource-id', resource_id, index, root_node, is_capture)

    def check_resource_id(self, resource_id: str, index: int = 0, root_node: ui_node.UINode = None, is_capture: bool = False) -> bool:
        node = self.find_resource_id(resource_id, index, root_node, is_capture)
        return node is not None

    def touch_resource_id(self, resource_id: str, index: int = 0, root_node: ui_node.UINode = None, is_capture: bool = False) -> bool:
        node = self.find_resource_id(resource_id, index, root_node, is_capture)
        if node is None:
            return False
        ret = self.adb.query(
            f'shell input tap {node.center[0]} {node.center[1]}')
        return ret.returncode == 0

    def find_node(self, attribute_name: str, search_text: str, index: int = 0, root_node: ui_node.UINode = None, is_capture: bool = False) -> ui_node.UINode:
        if is_capture:
            self.capture()

        if root_node is None:
            root_node = self.content_tree

        nodes = self.find_nodes(attribute_name, search_text, root_node)
        if index >= len(nodes):
            return None

        return nodes[index]

    def find_nodes(self, attribute_name: str, search_text: str, root_node: ui_node.UINode) -> list[ui_node.UINode]:
        nodes = []

        if getattr(root_node, attribute_name, None) == search_text:
            nodes.append(root_node)

        for child in root_node.children:
            child_nodes = self.find_nodes(attribute_name, search_text, child)
            nodes.extend(child_nodes)

        return nodes
