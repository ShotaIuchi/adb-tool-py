import io
import os
import subprocess
import tempfile
from typing import Optional

import numpy as np
import adb_tool_py as adb_tool
import adb_tool_py.ui_node as ui_node


class LogcatContext:
    """
    A context manager for handling logcat subprocesses and output files.
    """

    def __init__(self, subprocess: subprocess.Popen, file: io.TextIOWrapper, is_delete: bool = True):
        """
        Initializes the LogcatContext class.

        :param subprocess: The logcat subprocess.
        :param file: The file to which logcat output is written.
        :param is_delete: Whether to delete the file upon exit, defaults to True.
        """
        self.subprocess = subprocess
        self.file = file
        self.is_delete = is_delete

    def __enter__(self):
        """
        Enters the context and returns the LogcatContext instance.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exits the context, closing the file and terminating the subprocess.
        """
        self.close()

    def open(self, mode: str = 'r') -> io.TextIOWrapper:
        """
        Opens the logcat output file.

        :param mode: The mode in which to open the file, defaults to 'r'.
        :return: The opened file.
        """
        return open(self.file.name, mode)

    def close(self) -> None:
        """
        Closes the logcat output file and terminates the subprocess.
        """
        self.file.close()
        if self.is_delete:
            os.remove(self.file.name)
        self.subprocess.terminate()
        self.subprocess.wait()


class AdbTool:
    """
    A class to interact with an Android device using ADB commands and UI interactions.
    """

    def __init__(self, adb_command: Optional[adb_tool.AdbCommand] = None, adb: str = "adb", serial: Optional[str] = None):
        """
        Initializes the AdbTool class.

        :param adb_command: An instance of ADB command interface, defaults to None.
        :param adb: Path to the ADB executable, defaults to "adb".
        :param serial: The serial number of the target device, defaults to None.
        """
        self.adb = adb_command
        if adb_command is None:
            self.adb = adb_tool.AdbCommand(adb, adb_tool.AdbDevice(serial))
        self.avt = adb_tool.AdbViewTree(self.adb)
        self.aic = adb_tool.AdbImageCV(self.adb)

    def query(self, cmd: str, stdout=subprocess.PIPE, stderr=subprocess.PIPE) -> subprocess.CompletedProcess:
        """
        Executes an ADB command and waits for it to complete.

        :param cmd: The command to execute.
        :param stdout: Standard output pipe, defaults to subprocess.PIPE.
        :param stderr: Standard error pipe, defaults to subprocess.PIPE.
        :return: The completed process.
        """
        return self.adb.query(cmd, stdout, stderr)

    def query_async(self, cmd: str, stdout=subprocess.PIPE, stderr=subprocess.PIPE) -> subprocess.Popen:
        """
        Executes an ADB command asynchronously.

        :param cmd: The command to execute.
        :param stdout: Standard output pipe, defaults to subprocess.PIPE.
        :param stderr: Standard error pipe, defaults to subprocess.PIPE.
        :return: The process object.
        """
        return self.adb.query_async(cmd, stdout, stderr)

    def logcat(self, output_file: Optional[io.TextIOWrapper] = None, cmd: str = '') -> LogcatContext:
        """
        Starts a logcat subprocess and returns a LogcatContext for managing it.

        :param output_file: The file to which logcat output is written, defaults to None.
        :param cmd: Additional logcat command options, defaults to an empty string.
        :return: A LogcatContext instance.
        """
        is_delete = False
        if output_file is None:
            output_file = tempfile.NamedTemporaryFile(delete=False)
            is_delete = True
        sp = self.query_async(['logcat', *cmd.split(' ')], stdout=output_file)
        return LogcatContext(sp, output_file, is_delete)

    def logcat_clear(self, cmd: str = '') -> subprocess.CompletedProcess:
        """
        Clears the logcat logs on the device.

        :param cmd: Additional logcat command options, defaults to an empty string.
        :return: The completed process.
        """
        return self.query(['logcat', '-c', *cmd.split(' ')])

    def logcat_dump(self, cmd: str = '') -> subprocess.CompletedProcess:
        """
        Dumps the logcat logs from the device.

        :param cmd: Additional logcat command options, defaults to an empty string.
        :return: The completed process.
        """
        return self.query(['logcat', '-d', *cmd.split(' ')])

    def capture_tree(self) -> None:
        """
        Captures the current UI hierarchy of the connected Android device.
        """
        self.avt.capture()

    def capture_screenshot(self) -> None:
        """
        Captures the current screen of the connected Android device.
        """
        self.aic.capture()

    def content_tree(self) -> ui_node.UINode:
        """
        Returns the root node of the captured UI hierarchy.

        :return: The root UINode.
        """
        return self.avt.content_tree

    def content_screen(self) -> np.ndarray:
        """
        Returns the captured screen as an OpenCV image.

        :return: The captured screen as an OpenCV image.
        """
        return self.aic.content_cv

    def find_texts(self, text: str, root_node: Optional[ui_node.UINode] = None, is_capture: bool = False) -> list[ui_node.UINode]:
        """
        Finds nodes by their text attribute.

        :param text: The text to search for.
        :param root_node: The root node to start the search from, defaults to None.
        :param is_capture: Whether to capture the UI hierarchy before searching, defaults to False.
        :return: A list of matching UINodes.
        """
        return self.avt.find_texts(text, root_node, is_capture)

    def find_text(self, text: str, index: int = 0, root_node: Optional[ui_node.UINode] = None, is_capture: bool = False) -> Optional[ui_node.UINode]:
        """
        Finds a node by its text attribute.

        :param text: The text to search for.
        :param index: The index of the matching node to return, defaults to 0.
        :param root_node: The root node to start the search from, defaults to None.
        :param is_capture: Whether to capture the UI hierarchy before searching, defaults to False.
        :return: The matching UINode, or None if not found.
        """
        return self.avt.find_text(text, index, root_node, is_capture)

    def find_resource_id(self, resource_id: str, index: int = 0, root_node: Optional[ui_node.UINode] = None, is_capture: bool = False) -> Optional[ui_node.UINode]:
        """
        Finds a node by its resource-id attribute.

        :param resource_id: The resource-id to search for.
        :param index: The index of the matching node to return, defaults to 0.
        :param root_node: The root node to start the search from, defaults to None.
        :param is_capture: Whether to capture the UI hierarchy before searching, defaults to False.
        :return: The matching UINode, or None if not found.
        """
        return self.avt.find_resource_id(resource_id, index, root_node, is_capture)

    def check_text(self, text: str, index: int = 0, root_node: Optional[ui_node.UINode] = None, is_capture: bool = False) -> bool:
        """
        Checks if a node with the specified text exists.

        :param text: The text to search for.
        :param index: The index of the matching node to return, defaults to 0.
        :param root_node: The root node to start the search from, defaults to None.
        :param is_capture: Whether to capture the UI hierarchy before searching, defaults to False.
        :return: True if the node exists, False otherwise.
        """
        return self.avt.check_text(text, index, root_node, is_capture)

    def check_resource_id(self, resource_id: str, index: int = 0, root_node: Optional[ui_node.UINode] = None, is_capture: bool = False) -> bool:
        """
        Checks if a node with the specified resource-id exists.

        :param resource_id: The resource-id to search for.
        :param index: The index of the matching node to return, defaults to 0.
        :param root_node: The root node to start the search from, defaults to None.
        :param is_capture: Whether to capture the UI hierarchy before searching, defaults to False.
        :return: True if the node exists, False otherwise.
        """
        return self.avt.check_resource_id(resource_id, index, root_node, is_capture)

    def touch_text(self, text: str, index: int = 0, root_node: Optional[ui_node.UINode] = None, is_capture: bool = False) -> bool:
        """
        Simulates a tap on the node with the specified text.

        :param text: The text to search for.
        :param index: The index of the matching node to return, defaults to 0.
        :param root_node: The root node to start the search from, defaults to None.
        :param is_capture: Whether to capture the UI hierarchy before searching, defaults to False.
        :return: True if the tap was successful, False otherwise.
        """
        return self.avt.touch_text(text, index, root_node, is_capture)

    def touch_resource_id(self, resource_id: str, index: int = 0, root_node: Optional[ui_node.UINode] = None, is_capture: bool = False) -> bool:
        """
        Simulates a tap on the node with the specified resource-id.

        :param resource_id: The resource-id to search for.
        :param index: The index of the matching node to return, defaults to 0.
        :param root_node: The root node to start the search from, defaults to None.
        :param is_capture: Whether to capture the UI hierarchy before searching, defaults to False.
        :return: True if the tap was successful, False otherwise.
        """
        return self.avt.touch_resource_id(resource_id, index, root_node, is_capture)

    def find_images(self, image_path: str, match_threshold: float = 0.99, merge_threshold: int = 10) -> list[tuple[int, int, int, int]]:
        """
        Finds instances of a specified image within the captured screen image.

        :param image_path: Path to the image file to search for.
        :param match_threshold: Threshold for image matching, defaults to 0.99.
        :param merge_threshold: Threshold for merging close rectangles, defaults to 10.
        :return: A list of rectangles where the image was found.
        """
        return self.aic.find_images(image_path, match_threshold, merge_threshold)

    def find_image(self, image_path: str, index: int = 0, is_capture: bool = False, match_threshold: float = 0.99, merge_threshold: int = 10) -> Optional[tuple[int, int, int, int]]:
        """
        Finds the specified image on the screen and returns the rectangle of the match.

        :param image_path: Path to the image file to search for.
        :param index: Index of the matching image rectangle to return, defaults to 0.
        :param is_capture: Whether to capture the screen before searching, defaults to False.
        :param match_threshold: Threshold for image matching, defaults to 0.99.
        :param merge_threshold: Threshold for merging close rectangles, defaults to 10.
        :return: The rectangle of the found image, or None if not found.
        """
        return self.aic.find_image(image_path, index, is_capture, match_threshold, merge_threshold)

    def touch_image(self, image_path: str, index: int = 0, is_capture: bool = False, match_threshold: float = 0.99, merge_threshold: int = 10) -> bool:
        """
        Simulates a tap on the screen at the center of the specified image if found.

        :param image_path: Path to the image file to search for.
        :param index: Index of the matching image rectangle to use, defaults to 0.
        :param is_capture: Whether to capture the screen before searching, defaults to False.
        :param match_threshold: Threshold for image matching, defaults to 0.99.
        :param merge_threshold: Threshold for merging close rectangles, defaults to 10.
        :raises ValueError: If the image is not found.
        :return: True if the tap was successful, False otherwise.
        """
        return self.aic.touch_image(image_path, index, is_capture, match_threshold, merge_threshold)

    def check_image(self, image_path: str, index: int = 0, is_capture: bool = False, match_threshold: float = 0.99, merge_threshold: int = 10) -> bool:
        """
        Checks if the specified image is present on the screen.

        :param image_path: Path to the image file to search for.
        :param index: Index of the matching image rectangle to use, defaults to 0.
        :param is_capture: Whether to capture the screen before searching, defaults to False.
        :param match_threshold: Threshold for image matching, defaults to 0.99.
        :param merge_threshold: Threshold for merging close rectangles, defaults to 10.
        :return: True if the image is found, False otherwise.
        """
        return self.aic.check_image(image_path, index, is_capture, match_threshold, merge_threshold)
