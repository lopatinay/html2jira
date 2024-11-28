from abc import ABC, abstractmethod

from bs4 import NavigableString, Tag

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


class DivConverter(TagConverterStrategy):
    tag_name = 'div'

    def convert(self, tag) -> str:
        return tag.decode_contents() + "\n"


class ULConverter(TagConverterStrategy):
    tag_name = 'ul'

    def convert(self, tag, process_node, depth):
        result = ''

        for child in tag.contents:
            if isinstance(child, Tag) and child.name == 'li':
                r = LIConverter().convert(child, process_node, depth + 1)
                result += f"\n{r}"
            else:
                result += process_node(child, depth)
        return result


class OLConverter(TagConverterStrategy):
    tag_name = 'ol'

    def convert(self, tag, process_node, depth):
        result = ''

        for child in tag.contents:
            if isinstance(child, Tag) and child.name == 'li':
                r = LIConverter().convert(child, process_node, depth + 1)
                result += f"\n{r}"
            else:
                result += process_node(child, depth)
        return result


class LIConverter(TagConverterStrategy):
    tag_name = 'li'

    def convert(self, tag, process_node, depth):
        if tag.parent.name == 'ol':
            prefix_char = '#'
        else:
            prefix_char = '*'

        indent = prefix_char * depth

        # Обрабатываем содержимое элемента <li>
        content = ''
        for child in tag.contents:
            if isinstance(child, Tag) and child.name in ['ul', 'ol']:
                if child.name == 'ul':
                    content += ULConverter().convert(child, process_node, depth)
                elif child.name == 'ol':
                    content += OLConverter().convert(child, process_node, depth)
            else:
                content += process_node(child, depth)

        result = f"{indent} {content}"
        return result


class TableConverter(TagConverterStrategy):
    tag_name = 'table'

    def convert(self, tag, process_node, depth) -> str:
        result = ""
        for child in tag.contents:
            if child.name in {'thead', 'tbody'}:
                for sub_child in child.contents:
                    if isinstance(sub_child, Tag) and sub_child.name == 'tr':
                        result += RowConverter().convert(sub_child, process_node) + "\n"
            else:
                if isinstance(child, Tag) and child.name == 'tr':
                    result += RowConverter().convert(child, process_node) + "\n"
                else:
                    result += process_node(child)

        return result


class RowConverter(TagConverterStrategy):
    tag_name = 'tr'

    def convert(self, tag, process_node) -> str:
        is_header_row = False

        row_content = ""
        for child in tag.children:
            if isinstance(child, Tag) and child.name == 'td':
                row_content += "|"
                row_content += CellConverter().convert(child, process_node)
            elif isinstance(child, Tag) and child.name == 'th':
                is_header_row = Tag
                row_content += "||"
                row_content += HeaderCellConverter().convert(child, process_node)

        row_content += "||" if is_header_row else "|"
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
        return f"h1. {tag.text}{self.get_styles(tag)}\n"


class H2Converter(TagConverterStrategy):
    tag_name = 'h2'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"h2. {content}{self.get_styles(tag)}\n"


class H3Converter(TagConverterStrategy):
    tag_name = 'h3'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"h3. {content}{self.get_styles(tag)}\n"


class H4Converter(TagConverterStrategy):
    tag_name = 'h4'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"h4. {content}{self.get_styles(tag)}\n"


class H5Converter(TagConverterStrategy):
    tag_name = 'h5'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"h5. {content}{self.get_styles(tag)}\n"


class H6Converter(TagConverterStrategy):
    tag_name = 'h6'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"h6. {content}{self.get_styles(tag)}\n"


class BConverter(TagConverterStrategy):
    tag_name = 'b'

    def convert(self, tag) -> str:
        return f"*{tag.text}*{self.get_styles(tag)}".strip()


class ParagraphConverter(TagConverterStrategy):
    tag_name = 'p'

    def convert(self, tag) -> str:
        return f"\n{tag.decode_contents()}{self.get_styles(tag)}\n"


class AnchorConverter(TagConverterStrategy):
    tag_name = 'a'

    def convert(self, tag) -> str:
        href = tag.get('href', '#')
        text = tag.text.strip() or "link"

        if "#" in href:
            return f"[#{text}]{self.get_styles(tag)}".strip()
        elif "mailto" in href:
            return f"[{href}]{self.get_styles(tag)}".strip()
        elif "file" in href:
            return f"[{href}]{self.get_styles(tag)}".strip()
        return f"[{text}|{href}]{self.get_styles(tag)}".strip()


class IConverter(TagConverterStrategy):
    tag_name = 'i'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"_{content}_{self.get_styles(tag)}".strip()


class ImgConverter(TagConverterStrategy):
    tag_name = 'img'

    def convert(self, tag) -> str:
        src = tag.get('src', '#')
        alt = tag.get('alt', 'image')
        return f"!{src}|alt={alt}!{self.get_styles(tag)}".strip()


class CodeConverter(TagConverterStrategy):
    tag_name = 'code'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"{{code}}\n{content}\n{{code}}{self.get_styles(tag)}"


class InsertedConverter(TagConverterStrategy):
    tag_name = 'u'

    def convert(self, tag) -> str:
        text = tag.text.strip()

        return f"+{text}+{self.get_styles(tag)}".strip()


class AbbreviationConverter(TagConverterStrategy):
    tag_name = 'abbr'

    def convert(self, tag) -> str:
        text = tag.text.strip()

        return f"_({text})_{self.get_styles(tag)}".strip()


class AcronymConverter(TagConverterStrategy):
    tag_name = 'acronym'

    def convert(self, tag) -> str:
        text = tag.text.strip()
        return f"*{text}*{self.get_styles(tag)}".strip()


class AddressConverter(TagConverterStrategy):
    tag_name = 'address'

    def convert(self, tag) -> str:
        content = tag.decode_contents().strip()
        return f"\n{{quote}}\n{content}{self.get_styles(tag)}\n{{quote}}\n".strip()


class BDOConverter(TagConverterStrategy):
    tag_name = 'bdo'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        direction = tag.get("dir", "").lower()

        if direction == "rtl":
            return f"{{direction:rtl}}{content}{{direction}}{self.get_styles(tag)}".strip()
        elif direction == "ltr":
            return f"{{direction:ltr}}{content}{{direction}}{self.get_styles(tag)}".strip()
        return f"{content}{self.get_styles(tag)}".strip()


class BigConverter(TagConverterStrategy):
    tag_name = 'big'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"{{+{content}+}}{self.get_styles(tag)}".strip()


class BlockquoteConverter(TagConverterStrategy):
    tag_name = 'blockquote'

    def convert(self, tag) -> str:
        content = tag.decode_contents().strip()
        return f"bq. {content}{self.get_styles(tag)}".strip()


class QuoteConverter(TagConverterStrategy):
    tag_name = 'q'

    def convert(self, tag) -> str:
        content = tag.decode_contents().strip()
        s = self.get_styles(tag)
        return f"\n{{quote}}\n{content}\n{{quote}}\n".strip()



class CaptionConverter(TagConverterStrategy):
    tag_name = 'caption'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"{{center}}{content}{self.get_styles(tag)}{{center}}".strip()


class CiteConverter(TagConverterStrategy):
    tag_name = 'cite'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"??{content}??{self.get_styles(tag)}".strip()


class DDConverter(TagConverterStrategy):
    tag_name = 'dd'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f" : {content}{self.get_styles(tag)}".strip()


class DelConverter(TagConverterStrategy):
    tag_name = 'del'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"-{content}-{self.get_styles(tag)}".strip()


class DfnConverter(TagConverterStrategy):
    tag_name = 'dfn'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"_{content}_{self.get_styles(tag)}".strip()


class DlConverter(TagConverterStrategy):
    tag_name = 'dl'

    def convert(self, tag) -> str:
        content = tag.decode_contents().strip()
        return f"{{quote}}\n{content}{self.get_styles(tag)}\n{{quote}}".strip()


class DTConverter(TagConverterStrategy):
    tag_name = 'dt'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"*{content}*{self.get_styles(tag)}".strip()


class EmConverter(TagConverterStrategy):
    tag_name = 'em'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"_{content}_{self.get_styles(tag)}".strip()


class SampConverter(TagConverterStrategy):
    tag_name = 'samp'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"{{{{{content}}}}}{self.get_styles(tag)}".strip()


class SpanConverter(TagConverterStrategy):
    tag_name = 'span'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"{content}{self.get_styles(tag)}".strip()


class StrikeConverter(TagConverterStrategy):
    tag_name = 'strike'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"-{content}-{self.get_styles(tag)}".strip()


class StrongConverter(TagConverterStrategy):
    tag_name = 'strong'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"*{content}*{self.get_styles(tag)}".strip()


class SubConverter(TagConverterStrategy):
    tag_name = 'sub'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"~{content}~{self.get_styles(tag)}".strip()


class SupConverter(TagConverterStrategy):
    tag_name = 'sup'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"^{content}^{self.get_styles(tag)}".strip()


class HRConverter(TagConverterStrategy):
    tag_name = 'hr'

    def convert(self, tag) -> str:
        return f"\n----{self.get_styles(tag)}\n"


class InsConverter(TagConverterStrategy):
    tag_name = 'ins'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"+{content}+{self.get_styles(tag)}".strip()


class KbdConverter(TagConverterStrategy):
    tag_name = 'kbd'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"{{{{{content}}}}}{self.get_styles(tag)}".strip()


class PreConverter(TagConverterStrategy):
    tag_name = 'pre'

    def convert(self, tag) -> str:
        content = tag.decode_contents().strip()
        return f"{{{{{content}}}}}{self.get_styles(tag)}".strip()


class VarConverter(TagConverterStrategy):
    tag_name = 'var'

    def convert(self, tag) -> str:
        content = tag.text.strip()
        return f"_{content}_{self.get_styles(tag)}".strip()


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
