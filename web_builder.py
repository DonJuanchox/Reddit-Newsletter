class HTMLElement:
    def __init__(self, tag, content="", **attributes):
        self.tag = tag
        self.content = content
        # Convert 'class_' to 'class' for valid HTML attributes
        self.attributes = {k.rstrip('_'): v for k, v in attributes.items()}
        self.children = []

    def add_child(self, child):
        if isinstance(child, HTMLElement):
            self.children.append(child)
        else:
            self.children.append(HTMLElement("span", str(child)))

    def set_attribute(self, key, value):
        self.attributes[key] = value

    def render(self):
        attrs = " ".join(f'{key}="{value}"' for key, value in self.attributes.items())
        if attrs:
            attrs = " " + attrs
        children_html = "".join(child.render() for child in self.children)
        return f"<{self.tag}{attrs}>{self.content}{children_html}</{self.tag}>"

    def __str__(self):
        return self.render()