from abc import ABC, abstractmethod


class StyleHandler(ABC):
    @abstractmethod
    def process(self, styles: dict) -> str:
        pass


class ColorStyleHandler(StyleHandler):
    def process(self, styles: dict) -> str:
        if "color" in styles:
            return f"(color: {styles['color']})"
        return ""


class BackgroundColorStyleHandler(StyleHandler):
    def process(self, styles: dict) -> str:
        if "background-color" in styles:
            return f"(background: {styles['background-color']})"
        return ""


class StyleProcessor:
    def __init__(self):
        self.handlers = []

    def register_handler(self, handler: StyleHandler):
        self.handlers.append(handler)

    def process_styles(self, style: str) -> str:
        styles = self._parse_style(style)
        results = [handler.process(styles) for handler in self.handlers]
        return " ".join(filter(None, results))

    @staticmethod
    def _parse_style(style: str) -> dict:
        if not style:
            return {}
        styles = {}
        for rule in style.split(";"):
            if ":" in rule:
                key, value = rule.split(":", 1)
                styles[key.strip()] = value.strip()
        return styles
