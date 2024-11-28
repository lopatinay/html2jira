import re

from bs4 import BeautifulSoup, NavigableString, Tag

from tag_converter.tag_converter_strategy import StrategyRegistry, TagConverterStrategy


class HtmlToJiraWikiConverter:
    def __init__(self, registry: StrategyRegistry):
        self.registry = registry

    def convert(self, html_content: str) -> str:
        html = "".join(line.strip() for line in html_content.split("\n"))
        soup = BeautifulSoup(html, "html.parser")

        if soup.body is None:
            body_tag = soup.new_tag('body')
            body_tag.extend(soup.contents)
            soup.clear()
            soup.append(body_tag)
            return self.process_node(body_tag)
        else:
            return self.process_node(soup.body)

    def process_node(self, node, depth=0):
        if isinstance(node, NavigableString):
            text = node.text
            return text

        # Processing child nodes
        for child in node.children:
            if child.name in {"ul", "ol", "table"}:
                strategy = self.registry.get_strategy(child.name)
                result = strategy.convert(child, self.process_node, depth) + "\n\n"
            else:
                result = self.process_node(child)
            if isinstance(result, str):
                new_child = NavigableString(result)
                child.replace_with(new_child)
            elif isinstance(result, (Tag, NavigableString)):
                child.replace_with(result)
            else:
                child.extract()

        # Processing current node
        if strategy := self.registry.get_strategy(node.name):
            return strategy.convert(node)
        # If there is no strategy, return the text content of the node
        return node.get_text()


if __name__ == "__main__":
    class CustomImgConverter(TagConverterStrategy):
        tag_name = 'img'

        def convert(self, tag) -> str:
            return "[^Jira.png]"

    registry = StrategyRegistry()
    registry.register_all()
    registry.register("img", CustomImgConverter())
    converter = HtmlToJiraWikiConverter(registry)

    with open("templates/combination.html") as fd:
        jira_wiki = converter.convert(fd.read())
        print(jira_wiki)
