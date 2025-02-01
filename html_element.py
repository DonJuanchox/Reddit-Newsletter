"""
This module defines the `HTMLElement` class, which provides a structured way to create and manage HTML elements dynamically in Python.

The class allows:
- Representation of an HTML element with tag, attributes, content, and child elements.
- Adding child elements, either as `HTMLElement` objects or plain text wrapped in `<span>` tags.
- Setting and modifying HTML attributes dynamically.
- Rendering the complete HTML structure as a string.

Example Usage:
    >>> div = HTMLElement("div", "Hello, world!", class_="container")
    >>> div.add_child(HTMLElement("p", "This is a paragraph."))
    >>> print(div)
    '<div class="container">Hello, world!<p>This is a paragraph.</p></div>'

This module is useful for dynamically generating HTML structures within Python applications.
"""
from typing import Any, Dict, List, Optional, Union

class HTMLElement:
    """
    A class representing an HTML element.

    Attributes:
        tag (str): The HTML tag name (e.g., "div", "p", "a").
        content (str): The inner text content of the element.
        attributes (Dict[str, str]): Dictionary of HTML attributes and their values.
        children (List[HTMLElement]): List of child elements.
    """

    def __init__(self, tag: str, content: str = "", **attributes: Optional[str]) -> None:
        """
        Initializes an HTMLElement with a tag, optional content, and attributes.

        Args:
            tag (str): The HTML tag name (e.g., "div", "p", "a").
            content (str, optional): The text content of the element. Default is an empty string.
            **attributes (Optional[str]): Additional HTML attributes (e.g., class="container", id="main").
        """
        self.tag: str = tag
        self.content: str = content
        self.attributes: Dict[str, str] = {k.rstrip('_'): v for k, v in attributes.items() if v is not None}
        self.children: List[HTMLElement] = []

    def add_child(self, child: Union["HTMLElement", str]) -> None:
        """
        Adds a child element to this HTMLElement.

        - If `child` is a string, it is wrapped in a `<span>` tag.
        - If `child` is an `HTMLElement`, it is added as a direct child.

        Args:
            child (Union[HTMLElement, str]): The child element or text to be added.
        """
        self.children.append(child if isinstance(child, HTMLElement) else HTMLElement("span", str(child)))

    def set_attribute(self, key: str, value: Optional[str]) -> None:
        """
        Sets an attribute for the HTML element.

        Args:
            key (str): The name of the attribute (e.g., "class", "id").
            value (Optional[str]): The value of the attribute. If None, the attribute is not set.
        """
        if value is not None:
            self.attributes[key.rstrip('_')] = value

    def render(self) -> str:
        """
        Generates and returns the HTML string representation of the element.

        Returns:
            str: The complete HTML representation of the element and its children.
        """
        attrs: str = " ".join(f'{key}="{value}"' for key, value in self.attributes.items())
        children_html: str = "".join(child.render() for child in self.children)
        return f"<{self.tag} {attrs}>{self.content}{children_html}</{self.tag}>"

    def __str__(self) -> str:
        """
        Returns:
            str: The string representation of the HTMLElement (calls `render()`).
        """
        return self.render()
