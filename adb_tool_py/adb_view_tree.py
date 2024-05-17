import chardet
import os
import tempfile
import xml.etree.ElementTree as ET
import adb_tool_py as adb_tool
import adb_tool_py.ui_node as ui_node


DEVICE_FILE_PATH = '/sdcard/window_dump.xml'


def _parse_uiautomator_tree(content: str) -> ui_node.UINode:
    """
    Parses the UI Automator XML content into a UINode tree structure.

    :param content: The XML content as a string.
    :return: The root UINode of the parsed tree.
    """
    root_element = ET.fromstring(content)
    root_node = ui_node.UINode(root_element)
    _build_tree(root_element, root_node)
    return root_node


def _build_tree(element: ET.Element, current_node: ui_node.UINode) -> None:
    """
    Recursively builds the UINode tree from the XML elements.

    :param element: The current XML element.
    :param current_node: The current UINode.
    """
    for child_element in element:
        if child_element.tag == 'node':
            child_node = ui_node.UINode(child_element, parent=current_node)
            current_node.add_child(child_node)
            _build_tree(child_element, child_node)


class AdbViewTree:
    """
    A class to capture and interact with the UI hierarchy of an Android device.
    """
    content: str = None
    content_tree: ui_node.UINode = None

    def __init__(self, adb: adb_tool.AdbCommand = adb_tool.AdbCommand()):
        """
        Initializes the AdbViewTree class.

        :param adb: An instance of ADB command interface, defaults to adb_tool.AdbCommand().
        """
        self.adb = adb

    def capture(self) -> None:
        """
        Captures the current UI hierarchy of the connected Android device.
        """
        # Capture UI hierarchy dump
        ret = self.adb.query(f'shell uiautomator dump {DEVICE_FILE_PATH}')
        if ret.returncode != 0:
            raise Exception(f"Error: {ret.stderr.decode()}")

        # Pull the dump file from the device
        with tempfile.NamedTemporaryFile(delete=False) as file:
            ret = self.adb.query(f'pull {DEVICE_FILE_PATH} {file.name}')
            if ret.returncode != 0:
                os.remove(file.name)
                raise Exception(f"Error: {ret.stderr.decode()}")

        # Detect file encoding
        with open(file.name, 'rb') as file:
            raw_data = file.read()
            encoding = chardet.detect(raw_data)['encoding']

        # Read content
        with open(file.name, 'r', encoding=encoding) as file:
            content = file.read()

        os.remove(file.name)
        self.content = content
        self.content_tree = _parse_uiautomator_tree(content)

    def find_text(self, text: str, index: int = 0, root_node: ui_node.UINode = None, is_capture: bool = False) -> ui_node.UINode:
        """
        Finds a node by its text attribute.

        :param text: The text to search for.
        :param index: The index of the matching node to return, defaults to 0.
        :param root_node: The root node to start the search from, defaults to None.
        :param is_capture: Whether to capture the UI hierarchy before searching, defaults to False.
        :return: The matching UINode.
        """
        return self.find_node('text', text, index, root_node, is_capture)

    def check_text(self, text: str, index: int = 0, root_node: ui_node.UINode = None, is_capture: bool = False) -> bool:
        """
        Checks if a node with the specified text exists.

        :param text: The text to search for.
        :param index: The index of the matching node to return, defaults to 0.
        :param root_node: The root node to start the search from, defaults to None.
        :param is_capture: Whether to capture the UI hierarchy before searching, defaults to False.
        :return: True if the node exists, False otherwise.
        """
        node = self.find_text(text, index, root_node, is_capture)
        return node is not None

    def touch_text(self, text: str, index: int = 0, root_node: ui_node.UINode = None, is_capture: bool = False) -> bool:
        """
        Simulates a tap on the node with the specified text.

        :param text: The text to search for.
        :param index: The index of the matching node to return, defaults to 0.
        :param root_node: The root node to start the search from, defaults to None.
        :param is_capture: Whether to capture the UI hierarchy before searching, defaults to False.
        :return: True if the tap was successful, False otherwise.
        """
        node = self.find_text(text, index, root_node, is_capture)
        if node is None:
            return False
        ret = self.adb.query(f'shell input tap {node.center[0]} {node.center[1]}')
        return ret.returncode == 0

    def find_resource_id(self, resource_id: str, index: int = 0, root_node: ui_node.UINode = None, is_capture: bool = False) -> ui_node.UINode:
        """
        Finds a node by its resource-id attribute.

        :param resource_id: The resource-id to search for.
        :param index: The index of the matching node to return, defaults to 0.
        :param root_node: The root node to start the search from, defaults to None.
        :param is_capture: Whether to capture the UI hierarchy before searching, defaults to False.
        :return: The matching UINode.
        """
        return self.find_node('resource-id', resource_id, index, root_node, is_capture)

    def check_resource_id(self, resource_id: str, index: int = 0, root_node: ui_node.UINode = None, is_capture: bool = False) -> bool:
        """
        Checks if a node with the specified resource-id exists.

        :param resource_id: The resource-id to search for.
        :param index: The index of the matching node to return, defaults to 0.
        :param root_node: The root node to start the search from, defaults to None.
        :param is_capture: Whether to capture the UI hierarchy before searching, defaults to False.
        :return: True if the node exists, False otherwise.
        """
        node = self.find_resource_id(resource_id, index, root_node, is_capture)
        return node is not None

    def touch_resource_id(self, resource_id: str, index: int = 0, root_node: ui_node.UINode = None, is_capture: bool = False) -> bool:
        """
        Simulates a tap on the node with the specified resource-id.

        :param resource_id: The resource-id to search for.
        :param index: The index of the matching node to return, defaults to 0.
        :param root_node: The root node to start the search from, defaults to None.
        :param is_capture: Whether to capture the UI hierarchy before searching, defaults to False.
        :return: True if the tap was successful, False otherwise.
        """
        node = self.find_resource_id(resource_id, index, root_node, is_capture)
        if node is None:
            return False
        ret = self.adb.query(f'shell input tap {node.center[0]} {node.center[1]}')
        return ret.returncode == 0

    def find_node(self, attribute_name: str, search_text: str, index: int = 0, root_node: ui_node.UINode = None, is_capture: bool = False) -> ui_node.UINode:
        """
        Finds a node by the specified attribute.

        :param attribute_name: The attribute name to search by.
        :param search_text: The text to search for.
        :param index: The index of the matching node to return, defaults to 0.
        :param root_node: The root node to start the search from, defaults to None.
        :param is_capture: Whether to capture the UI hierarchy before searching, defaults to False.
        :return: The matching UINode.
        """

        nodes = self.find_nodes(attribute_name, search_text, root_node, is_capture)
        if index >= len(nodes):
            return None

        return nodes[index]

    def find_nodes(self, attribute_name: str, search_text: str, root_node: ui_node.UINode, is_capture: bool = False) -> list[ui_node.UINode]:
        """
        Recursively finds all nodes with the specified attribute.

        :param attribute_name: The attribute name to search by.
        :param search_text: The text to search for.
        :param root_node: The root node to start the search from.
        :param is_capture: Whether to capture the UI hierarchy before searching, defaults to False.
        :return: A list of matching UINodes.
        """
        if is_capture:
            self.capture()

        if root_node is None:
            root_node = self.content_tree

        nodes = []

        if getattr(root_node, attribute_name, None) == search_text:
            nodes.append(root_node)

        for child in root_node.children:
            child_nodes = self.find_nodes(attribute_name, search_text, child)
            nodes.extend(child_nodes)

        return nodes
