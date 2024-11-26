from bs4 import BeautifulSoup, NavigableString

from tag_converter.tag_converter_strategy import StrategyRegistry


class HtmlToJiraWikiConverter:
    def __init__(self, registry: StrategyRegistry):
        self.registry = registry

    def convert(self, html_content: str) -> str:
        soup = BeautifulSoup(html_content, "html.parser")
        if soup.body is None:
            body_tag = soup.new_tag('body')
            body_tag.extend(soup.contents)
            soup.clear()
            soup.append(body_tag)
            return self.process_node(body_tag)
        else:
            return self.process_node(soup.body)

    def process_node(self, node, depth=0):
        result = ""

        if isinstance(node, NavigableString):
            text = str(node).strip()
            if text:
                return text
            else:
                return ''

        if strategy := self.registry.get_strategy(node.name):
            new_depth = depth + 1 if node.name in {'ul', 'ol'} else depth
            if strategy.tag_name in {"ul", "ol", "li"}:
                return strategy.convert(node, self.process_node, depth, new_depth)
            if strategy.tag_name in {"table", "thead", "tbody", "tr", "th", "td"}:
                return strategy.convert(node, self.process_node)
            return strategy.convert(node)
        else:
            for child in node.children:
                result += self.process_node(child, depth)
            return result


if __name__ == "__main__":
    registry = StrategyRegistry()
    registry.register_all()
    converter = HtmlToJiraWikiConverter(registry)

    with open("templates/lists.html") as fd:
        jira_wiki = converter.convert(fd.read())
        print(jira_wiki)
