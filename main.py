from bs4 import BeautifulSoup

from style_processor.style_processor import ColorStyleHandler, BackgroundColorStyleHandler, StyleProcessor
from tag_converter.tag_converter_strategy import HeadingConverter, ParagraphConverter, StrategyRegistry, \
    AnchorConverter, BreakLineConverter


class HtmlToJiraWikiConverter:
    def __init__(self, registry: StrategyRegistry):
        self.registry = registry

    def convert(self, html_content: str) -> str:
        soup = BeautifulSoup(html_content, "html.parser")
        # self.origin = soup.body.decode_contents().strip()
        r = self.process_node(soup.body)
        # print(self.origin)
        print(r)

    def process_node(self, node):
        result = ""

        if not node.find_all(recursive=False):
            if strategy := self.registry.get_strategy(node.name):
                return strategy.convert(node)
            return node if isinstance(node, str) else node.string or ""

        for child in node.children:
            if child.name:
                result += self.process_node(child)
            else:
                result += str(child)

        return result






if __name__ == "__main__":
    style_processor = StyleProcessor()
    style_processor.register_handler(ColorStyleHandler())
    style_processor.register_handler(BackgroundColorStyleHandler())

    registry = StrategyRegistry()
    registry.register("h1", HeadingConverter(style_processor))
    registry.register("p", ParagraphConverter(style_processor))
    registry.register("a", AnchorConverter(style_processor))
    registry.register("br", BreakLineConverter())

    html_content = """
    <body>
        <h1>Title</h1>
        <p>
            <p>This is a paragraph with <a href="localhost">my url</a> and other text</p>
            <p>foobar</p>
        </p>
    </body>
    """

    converter = HtmlToJiraWikiConverter(registry)
    jira_wiki = converter.convert(html_content)
