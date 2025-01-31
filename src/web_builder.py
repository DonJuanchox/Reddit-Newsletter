class HTMLElement:
    def __init__(self, tag, content="", **attributes):
        self.tag = tag
        self.content = content
        self.attributes = {k.rstrip('_'): v for k, v in attributes.items() if v is not None}
        self.children = []

    def add_child(self, child):
        """Add child elements, wrapping strings in span tags."""
        self.children.append(child if isinstance(child, HTMLElement) else HTMLElement("span", str(child)))

    def set_attribute(self, key, value):
        """Set an attribute if the value is not None."""
        if value is not None:
            self.attributes[key.rstrip('_')] = value

    def render(self):
        """Render HTML as a string."""
        attrs = " ".join(f'{key}="{value}"' for key, value in self.attributes.items())
        children_html = "".join(child.render() for child in self.children)
        return f"<{self.tag} {attrs}>{self.content}{children_html}</{self.tag}>"

    def __str__(self):
        return self.render()