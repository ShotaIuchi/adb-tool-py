import cv2
import numpy as np
import os
import tempfile
import adb_tool_py as adb_tool


class AdbImageCV:
    content = None
    content_cv: cv2 = None

    def __init__(self, adb: adb_tool.AdbCommand = adb_tool.AdbCommand()):
        self.adb = adb

    def capture(self) -> None:
        self.content = self._screencap()
        self.content_cv = cv2.imdecode(np.frombuffer(self.content, np.uint8), -1)

    def set_capture(self, image_path: str) -> None:
        with (open(image_path, 'rb')) as f:
            self.content = f.read()
        self.content_cv = cv2.imdecode(np.frombuffer(self.content, np.uint8), -1)

    def find_image(self, image_path: str, match_threshold: float = 0.99, merge_threshold: int = 10) -> list:
        if self.content is None:
            raise Exception("Please run the capture method first.")

        # read image
        with open(image_path, 'rb') as f:
            image = f.read()
        image_cv = cv2.imdecode(np.frombuffer(image, np.uint8), -1)
        image_h, image_w = image_cv.shape[:2]

        # matching
        result = cv2.matchTemplate(self.content_cv, image_cv, cv2.TM_CCOEFF_NORMED)

        # metch threshold over result
        locations = np.where(result >= match_threshold)

        # find rectangles
        rects = []
        for point in zip(*locations[::-1]):
            rect = (point[0], point[1], point[0] + image_w, point[1] + image_h)
            rects.append(rect)

        # merge rectangles
        rects = self._merge_rects(rects, merge_threshold)
        return rects

    def _screencap(self):
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_filepath = temp_file.name

        try:
            with open(temp_filepath, 'wb') as temp_file:
                self.adb.query('exec-out screencap -p', stdout=temp_file)

            with open(temp_filepath, 'rb') as temp_file:
                return temp_file.read()
        finally:
            try:
                os.remove(temp_filepath)
            except OSError as e:
                print(f"Error: {e.strerror}")

    def _merge_rects(self, rects: dict, threshold: int):
        if not rects:
            return []

        rects = sorted(rects, key=lambda x: (x[0], x[1]))
        merged_rects = []
        current_rect = rects[0]

        for rect in rects[1:]:
            if (abs(current_rect[0] - rect[0]) < threshold and
                    abs(current_rect[1] - rect[1]) < threshold and
                    abs(current_rect[2] - rect[2]) < threshold and
                    abs(current_rect[3] - rect[3]) < threshold):

                current_rect = (
                    min(current_rect[0], rect[0]),
                    min(current_rect[1], rect[1]),
                    max(current_rect[2], rect[2]),
                    max(current_rect[3], rect[3])
                )
            else:
                merged_rects.append(current_rect)
                current_rect = rect

        merged_rects.append(current_rect)
        return merged_rects
