from abc import ABC, abstractmethod

from style_processor.style_processor import StyleProcessor


class TagConverterStrategy(ABC):
    def __init__(self, style_processor: StyleProcessor = None):
        self.style_processor = style_processor

    @abstractmethod
    def convert(self, tag) -> str:
        pass


class HeadingConverter(TagConverterStrategy):
    def convert(self, tag) -> str:
        styles = self.style_processor.process_styles(tag.get("style", ""))
        return f"h1. {tag.text} {styles}".strip()


class ParagraphConverter(TagConverterStrategy):
    def convert(self, tag) -> str:
        styles = self.style_processor.process_styles(tag.get("style", ""))
        return f"\n{tag.decode_contents()} {styles}" + "\n"


class AnchorConverter(TagConverterStrategy):
    def convert(self, tag) -> str:
        href = tag.get('href', '#')
        text = tag.text.strip() or "link"
        styles = self.style_processor.process_styles(tag.get("style", ""))
        return f"[{text}]({href}) {styles}".strip()


class BreakLineConverter(TagConverterStrategy):
    def convert(self, tag) -> str:
        return "\n"


class StrategyRegistry:
    def __init__(self):
        self._strategies = {}

    def register(self, tag_name: str, strategy: TagConverterStrategy):
        self._strategies[tag_name] = strategy

    def get_strategy(self, tag_name: str):
        return self._strategies.get(tag_name)
