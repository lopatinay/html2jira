from abc import ABC, abstractmethod

from bs4 import NavigableString

from style_processor.style_processor import StyleProcessor


class TagConverterStrategy(ABC):
    __slots__ = ("style_processor",)
    tag_name = None
    nested = False

    def __init__(self, style_processor: StyleProcessor = None):
        self.style_processor = style_processor

    def get_styles(self, tag):
        return self.style_processor.process_styles(tag.get("style", ""))

    @abstractmethod
    def convert(self, tag) -> str:
        pass


class TableConverter(TagConverterStrategy):
    tag_name = 'table'

    def convert(self, tag, process_node) -> str:
        result = ""
        for child in tag.children:
            if child.name in ['thead', 'tbody', 'tr']:
                result += process_node(child)
        return result


class RowConverter(TagConverterStrategy):
    tag_name = 'tr'

    def convert(self, tag, process_node) -> str:
        is_header_row = any(child.name == 'th' for child in tag.children)
        row_content = ""
        for child in tag.children:
            if child.name in ['td', 'th']:
                cell_content = process_node(child).strip()
                separator = "||" if is_header_row else "|"
                row_content += f"{separator}{cell_content}"
        separator = "||" if is_header_row else "|"
        row_content += f"{separator}\n"
        return row_content


class CellConverter(TagConverterStrategy):
    tag_name = 'td'

    def convert(self, tag, process_node) -> str:
        content = ''.join(process_node(child) for child in tag.contents).strip()
        return content


class HeaderCellConverter(TagConverterStrategy):
    tag_name = 'th'

    def convert(self, tag, process_node) -> str:
        content = ''.join(process_node(child) for child in tag.contents).strip()
        return content


class HeadingConverter(TagConverterStrategy):
    tag_name = 'h1'

    def convert(self, tag) -> str:
        return f"h1. {tag.text} {self.get_styles(tag)}\n"


class H2Converter(TagConverterStrategy):
    tag_name = 'h2'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"h2. {content} {self.get_styles(tag)}\n"


class H3Converter(TagConverterStrategy):
    tag_name = 'h3'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"h3. {content} {self.get_styles(tag)}\n"


class H4Converter(TagConverterStrategy):
    tag_name = 'h4'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"h4. {content} {self.get_styles(tag)}\n"


class H5Converter(TagConverterStrategy):
    tag_name = 'h5'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"h5. {content} {self.get_styles(tag)}\n"


class H6Converter(TagConverterStrategy):
    tag_name = 'h6'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"h6. {content} {self.get_styles(tag)}\n"


class BoldConverter(TagConverterStrategy):
    tag_name = 'b'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"*{content}* {self.get_styles(tag)}".strip()


class ParagraphConverter(TagConverterStrategy):
    tag_name = 'p'

    def convert(self, tag) -> str:
        return f"\n{tag.decode_contents()} {self.get_styles(tag)}\n"


class AnchorConverter(TagConverterStrategy):
    tag_name = 'a'

    def convert(self, tag) -> str:
        href = tag.get('href', '#')
        text = tag.text.strip() or "link"

        return f"[{text}|{href}] {self.get_styles(tag)}".strip()


class IConverter(TagConverterStrategy):
    tag_name = 'i'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"_{content}_ {self.get_styles(tag)}".strip()


class ImgConverter(TagConverterStrategy):
    tag_name = 'img'

    def convert(self, tag) -> str:
        src = tag.get('src', '#')
        alt = tag.get('alt', 'image')
        return f"!{src}|alt={alt}! {self.get_styles(tag)}".strip()


class AbbreviationConverter(TagConverterStrategy):
    tag_name = 'abbr'

    def convert(self, tag) -> str:
        text = tag.text.strip()

        return f"_({text})_ {self.get_styles(tag)}".strip()


class AcronymConverter(TagConverterStrategy):
    tag_name = 'acronym'

    def convert(self, tag) -> str:
        text = tag.text.strip()
        return f"*{text}* {self.get_styles(tag)}".strip()


class AddressConverter(TagConverterStrategy):
    tag_name = 'address'

    def convert(self, tag) -> str:
        content = tag.decode_contents().strip()
        return f"\n{{quote}}\n{content} {self.get_styles(tag)}\n{{quote}}\n".strip()


class BDOConverter(TagConverterStrategy):
    tag_name = 'bdo'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        direction = tag.get("dir", "").lower()

        if direction == "rtl":
            return f"{{direction:rtl}}{content}{{direction}} {self.get_styles(tag)}".strip()
        elif direction == "ltr":
            return f"{{direction:ltr}}{content}{{direction}} {self.get_styles(tag)}".strip()
        return f"{content} {self.get_styles(tag)}".strip()


class BigConverter(TagConverterStrategy):
    tag_name = 'big'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"{{+{content}+}} {self.get_styles(tag)}".strip()


class BlockquoteConverter(TagConverterStrategy):
    tag_name = 'blockquote'

    def convert(self, tag) -> str:
        content = tag.decode_contents().strip()
        return f"\n{{quote}}\n{content} {self.get_styles(tag)}\n{{quote}}\n".strip()


class CaptionConverter(TagConverterStrategy):
    tag_name = 'caption'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"{{center}}{content} {self.get_styles(tag)}{{center}}".strip()


class CiteConverter(TagConverterStrategy):
    tag_name = 'cite'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"_{content}_ {self.get_styles(tag)}".strip()


class CodeConverter(TagConverterStrategy):
    tag_name = 'code'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"{{{{{content}}}}} {self.get_styles(tag)}".strip()


class DDConverter(TagConverterStrategy):
    tag_name = 'dd'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f" : {content} {self.get_styles(tag)}".strip()


class DelConverter(TagConverterStrategy):
    tag_name = 'del'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"-{content}- {self.get_styles(tag)}".strip()


class DfnConverter(TagConverterStrategy):
    tag_name = 'dfn'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"_{content}_ {self.get_styles(tag)}".strip()


class DivConverter(TagConverterStrategy):
    tag_name = 'div'

    def convert(self, tag) -> str:
        content = tag.decode_contents().strip()
        return f"{content} {self.get_styles(tag)}".strip()


class DlConverter(TagConverterStrategy):
    tag_name = 'dl'

    def convert(self, tag) -> str:
        content = tag.decode_contents().strip()
        return f"{{quote}}\n{content} {self.get_styles(tag)}\n{{quote}}".strip()


class DTConverter(TagConverterStrategy):
    tag_name = 'dt'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"*{content}* {self.get_styles(tag)}".strip()


class QConverter(TagConverterStrategy):
    tag_name = 'q'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"\"{content}\" {self.get_styles(tag)}".strip()


class EmConverter(TagConverterStrategy):
    tag_name = 'em'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"_{content}_ {self.get_styles(tag)}".strip()


class SampConverter(TagConverterStrategy):
    tag_name = 'samp'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"{{{{{content}}}}} {self.get_styles(tag)}".strip()


class SpanConverter(TagConverterStrategy):
    tag_name = 'span'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"{content} {self.get_styles(tag)}".strip()


class StrikeConverter(TagConverterStrategy):
    tag_name = 'strike'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"-{content}- {self.get_styles(tag)}".strip()


class StrongConverter(TagConverterStrategy):
    tag_name = 'strong'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"*{content}* {self.get_styles(tag)}".strip()


class SubConverter(TagConverterStrategy):
    tag_name = 'sub'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"{{sub:{content}}} {self.get_styles(tag)}".strip()


class SupConverter(TagConverterStrategy):
    tag_name = 'sup'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"{{sup:{content}}} {self.get_styles(tag)}".strip()


class HRConverter(TagConverterStrategy):
    tag_name = 'hr'

    def convert(self, tag) -> str:
        return f"---- {self.get_styles(tag)}".strip()


class InsConverter(TagConverterStrategy):
    tag_name = 'ins'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"+{content}+ {self.get_styles(tag)}".strip()


class KbdConverter(TagConverterStrategy):
    tag_name = 'kbd'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"{{{{{content}}}}} {self.get_styles(tag)}".strip()


class ULConverter(TagConverterStrategy):
    tag_name = 'ul'

    def convert(self, tag, process_node, depth, new_depth) -> str:
        result = ""
        for child in tag.children:
            result += process_node(child, new_depth)
        return result


class OLConverter(TagConverterStrategy):
    tag_name = 'ol'

    def convert(self, tag, process_node, depth, new_depth) -> str:
        result = ""
        for child in tag.children:
            result += process_node(child, new_depth)
        return result



class LIConverter(TagConverterStrategy):
    tag_name = 'li'

    def convert(self, tag, process_node, depth, new_depth) -> str:
        if tag.parent.name == "ol":
            prefix = "#"
        else:
            prefix = "*"

        content = ''
        for child in tag.contents:
            if isinstance(child, NavigableString):
                content += child
            elif child.name not in ['ul', 'ol']:
                content += process_node(child, depth)

        content = content.strip()
        indent = prefix * depth
        result = f"{indent} {content}\n"

        for child in tag.contents:
            if child.name in ['ul', 'ol']:
                result += process_node(child, depth)

        return result


class PreConverter(TagConverterStrategy):
    tag_name = 'pre'

    def convert(self, tag) -> str:
        content = tag.decode_contents().strip()
        return f"{{code}}\n{content}\n{{code}} {self.get_styles(tag)}"


class VarConverter(TagConverterStrategy):
    tag_name = 'var'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"_{content}_ {self.get_styles(tag)}".strip()


class BreakLineConverter(TagConverterStrategy):
    tag_name = 'br'

    def convert(self, tag) -> str:
        return "\n"


class StrategyRegistry:
    def __init__(self):
        self._strategies = {}

    def register(self, tag_name: str, strategy: TagConverterStrategy):
        self._strategies[tag_name] = strategy

    def register_all(self):
        style_processor = StyleProcessor()
        for child in TagConverterStrategy.__subclasses__():
            inst = child(style_processor)
            self.register(inst.tag_name, inst)

    def get_strategy(self, tag_name: str):
        return self._strategies.get(tag_name)
