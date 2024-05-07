import re


class UINode:
    def __init__(self, element, parent=None):
        self.element = element
        self.parent = parent
        self.children = []
        self._parse_attributes()

    def add_child(self, child) -> None:
        self.children.append(child)

    def __str__(self):
        return f"UINode(class={self.node_class}, resource_id={self.resource_id}, text={self.text}, children={len(self.children)})"

    def tree(self, level: int = 0) -> str:
        ret = "  " * level + str(self) + "\n"
        for child in self.children:
            ret += child.tree(level + 1)
        return ret

    def _parse_attributes(self) -> None:
        self.index = int(self.element.get('index', '0'))
        self.text = self.element.get('text', '')
        self.resource_id = self.element.get('resource-id', '')
        self.node_class = self.element.get('class', '')
        self.package = self.element.get('package', '')
        self.content_desc = self.element.get('content_desc', '')
        self.checkable = self.element.get(
            'checkable', 'false').lower() == 'true'
        self.checked = self.element.get('checked', 'false').lower() == 'true'
        self.clickable = self.element.get(
            'clickable', 'false').lower() == 'true'
        self.enabled = self.element.get('enabled', 'true').lower() == 'true'
        self.focusable = self.element.get(
            'focusable', 'false').lower() == 'true'
        self.focused = self.element.get('focused', 'false').lower() == 'true'
        self.scrollable = self.element.get(
            'scrollable', 'false').lower() == 'true'
        self.long_clickable = self.element.get(
            'long_clickable', 'false').lower() == 'true'
        self.password = self.element.get('password', 'false').lower() == 'true'
        self.selected = self.element.get('selected', 'false').lower() == 'true'
        self.bounds = self._parse_bounds(self.element.get('bounds', ''))
        if self.bounds:
            self.center = ((self.bounds[0] + self.bounds[2]) / 2,
                           (self.bounds[1] + self.bounds[3]) / 2)
        else:
            self.center = None

    def _parse_bounds(self, bounds_str) -> tuple[int, int, int, int]:
        match = re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', bounds_str)
        if match:
            return (int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4)))
        return None
