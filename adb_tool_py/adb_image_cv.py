from typing import Optional
import cv2
import numpy as np
import os
import tempfile
import adb_tool_py as adb_tool


class AdbImageCV:
    """
    A class to capture and process images from an Android device using ADB and OpenCV.
    """

    def __init__(self, adb: adb_tool.AdbCommand = adb_tool.AdbCommand()):
        """
        Initializes the AdbImageCV class with an optional ADB command object.

        :param adb: An instance of ADB command interface, defaults to adb_tool.AdbCommand().
        """
        self.adb = adb
        self.content: bytes = None
        self.content_cv: np.ndarray = None

    def capture(self) -> None:
        """
        Captures the current screen of the connected Android device and stores it as an OpenCV image.
        """
        try:
            self.content = self._screencap()
            self.content_cv = cv2.imdecode(np.frombuffer(self.content, np.uint8), -1)
        except Exception as e:
            raise RuntimeError("Failed to capture screen: " + str(e))

    def set_capture(self, image_path: str) -> None:
        """
        Sets the current capture from a specified image file path.

        :param image_path: Path to the image file.
        """
        try:
            with open(image_path, 'rb') as f:
                self.content = f.read()
            self.content_cv = cv2.imdecode(np.frombuffer(self.content, np.uint8), -1)
        except Exception as e:
            raise RuntimeError("Failed to set capture from image path: " + str(e))

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
        return self.find_image(image_path, index, is_capture, match_threshold, merge_threshold) is not None

    def touch_image(self, image_path: str, index: int = 0, is_capture: bool = False, match_threshold: float = 0.99, merge_threshold: int = 10) -> bool:
        """
        Simulates a tap on the screen at the center of the specified image if found.

        :param image_path: Path to the image file to search for.
        :param index: Index of the matching image rectangle to use, defaults to 0.
        :param is_capture: Whether to capture the screen before searching, defaults to False.
        :param match_threshold: Threshold for image matching, defaults to 0.99.
        :param merge_threshold: Threshold for merging close rectangles, defaults to 10.
        :raises ValueError: If the image is not found.
        """
        rect = self.find_image(image_path, index, is_capture, match_threshold, merge_threshold)

        if rect is None:
            return False

        x = (rect[0] + rect[2]) // 2
        y = (rect[1] + rect[3]) // 2
        result = self.adb.query(f'shell input tap {x} {y}')
        return result.returncode == 0

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
        rects = self.find_images(image_path, is_capture, match_threshold, merge_threshold)

        if len(rects) > index:
            return rects[index]

        return None

    def find_images(self, image_path: str, is_capture: bool = False, match_threshold: float = 0.99, merge_threshold: int = 10) -> list[tuple[int, int, int, int]]:
        """
        Finds instances of a specified image within the captured screen image.

        :param image_path: Path to the image file to search for.
        :param is_capture: Whether to capture the screen before searching, defaults to False.
        :param match_threshold: Threshold for image matching, defaults to 0.99.
        :param merge_threshold: Threshold for merging close rectangles, defaults to 10.
        :return: A list of rectangles where the image was found.
        """
        if is_capture:
            self.capture()

        if self.content is None:
            raise ValueError("Please run the capture method first.")

        try:
            # Read the image file to search for
            with open(image_path, 'rb') as f:
                image = f.read()
            # Convert the read image to an OpenCV image
            image_cv = cv2.imdecode(np.frombuffer(image, np.uint8), -1)
            image_h, image_w = image_cv.shape[:2]

            # Perform template matching to find the image in the captured screen
            result = cv2.matchTemplate(self.content_cv, image_cv, cv2.TM_CCOEFF_NORMED)

            # Identify locations where the match exceeds the threshold
            locations = np.where(result >= match_threshold)

            # Create rectangles for each matched location
            rects = [(point[0], point[1], point[0] + image_w, point[1] + image_h) for point in zip(*locations[::-1])]

            # Merge close rectangles to reduce redundancy
            rects = self._merge_rects(rects, merge_threshold)
            return rects
        except Exception as e:
            raise RuntimeError("Failed to find image: " + str(e))

    def _screencap(self) -> bytes:
        """
        Captures the screen of the connected Android device and returns the image as a byte array.

        :return: Byte array of the captured screen image.
        """
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_filepath = temp_file.name

        try:
            # Execute ADB screencap command and save the output to the temporary file
            with open(temp_filepath, 'wb') as temp_file:
                self.adb.query('exec-out screencap -p', stdout=temp_file)

            # Read the captured image from the temporary file
            with open(temp_filepath, 'rb') as temp_file:
                return temp_file.read()
        finally:
            # Delete the temporary file
            try:
                os.remove(temp_filepath)
            except OSError as e:
                print(f"Error deleting temporary file: {e.strerror}")

    def _merge_rects(self, rects: list[tuple[int, int, int, int]], threshold: int) -> list[tuple[int, int, int, int]]:
        """
        Merges close rectangles to reduce redundancy.

        :param rects: List of rectangles to merge.
        :param threshold: Threshold distance to merge rectangles.
        :return: List of merged rectangles.
        """
        if not rects:
            return []

        # Sort rectangles by their top-left coordinates
        rects = sorted(rects, key=lambda x: (x[0], x[1]))
        merged_rects = []
        current_rect = rects[0]

        for rect in rects[1:]:
            # Check if the current rectangle is close enough to merge
            if (abs(current_rect[0] - rect[0]) < threshold and
                    abs(current_rect[1] - rect[1]) < threshold and
                    abs(current_rect[2] - rect[2]) < threshold and
                    abs(current_rect[3] - rect[3]) < threshold):

                # Merge the current rectangle with the new one
                current_rect = (
                    min(current_rect[0], rect[0]),
                    min(current_rect[1], rect[1]),
                    max(current_rect[2], rect[2]),
                    max(current_rect[3], rect[3])
                )
            else:
                # Add the current rectangle to the merged list and move to the next one
                merged_rects.append(current_rect)
                current_rect = rect

        # Add the last rectangle
        merged_rects.append(current_rect)
        return merged_rects
