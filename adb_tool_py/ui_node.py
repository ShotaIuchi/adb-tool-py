import re
from typing import Optional, Tuple


class UINode:
    """
    A class to represent a UI node in an Android UI hierarchy.
    """

    def __init__(self, element, parent: Optional['UINode'] = None):
        """
        Initializes the UINode class.

        :param element: The XML element representing the UI node.
        :param parent: The parent UINode, defaults to None.
        """
        self.element = element
        self.parent = parent
        self.children = []
        self._parse_attributes()

    def add_child(self, child: 'UINode') -> None:
        """
        Adds a child node to this node.

        :param child: The child UINode to add.
        """
        self.children.append(child)

    def tree(self, level: int = 0) -> str:
        """
        Returns a string representation of the node tree.

        :param level: The current level in the tree, defaults to 0.
        :return: A string representation of the node tree.
        """
        ret = "  " * level + str(self) + "\n"
        for child in self.children:
            ret += child.tree(level + 1)
        return ret

    def _parse_attributes(self) -> None:
        """
        Parses the attributes of the XML element and sets them as attributes of the node.
        """
        self.index = int(self.element.get('index', '0'))
        self.text = self.element.get('text', '')
        self.resource_id = self.element.get('resource-id', '')
        self.node_class = self.element.get('class', '')
        self.package = self.element.get('package', '')
        self.content_desc = self.element.get('content-desc', '')
        self.checkable = self.element.get('checkable', 'false').lower() == 'true'
        self.checked = self.element.get('checked', 'false').lower() == 'true'
        self.clickable = self.element.get('clickable', 'false').lower() == 'true'
        self.enabled = self.element.get('enabled', 'true').lower() == 'true'
        self.focusable = self.element.get('focusable', 'false').lower() == 'true'
        self.focused = self.element.get('focused', 'false').lower() == 'true'
        self.scrollable = self.element.get('scrollable', 'false').lower() == 'true'
        self.long_clickable = self.element.get('long-clickable', 'false').lower() == 'true'
        self.password = self.element.get('password', 'false').lower() == 'true'
        self.selected = self.element.get('selected', 'false').lower() == 'true'
        self.bounds = self._parse_bounds(self.element.get('bounds', ''))
        if self.bounds:
            self.center = ((self.bounds[0] + self.bounds[2]) / 2,
                           (self.bounds[1] + self.bounds[3]) / 2)
        else:
            self.center = None

    def _parse_bounds(self, bounds_str: str) -> Optional[Tuple[int, int, int, int]]:
        """
        Parses the bounds attribute and returns it as a tuple.

        :param bounds_str: The bounds attribute as a string.
        :return: A tuple representing the bounds, or None if parsing fails.
        """
        match = re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', bounds_str)
        if match:
            return (int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4)))
        return None

    def __str__(self) -> str:
        """
        Returns a string representation of the node.

        :return: A string representation of the node.
        """
        return (f"UINode(class={self.node_class}, resource_id={self.resource_id}, "
                f"text={self.text}, children={len(self.children)})")
