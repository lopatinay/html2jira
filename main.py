import os

from html_to_jira.converter import HtmlToJiraWikiConverter
from tag_converter.tag_converter_strategy import StrategyRegistry, TagConverterStrategy


def client(html):
    class CustomImgConverter(TagConverterStrategy):
        tag_name = 'img'

        def convert(self, tag) -> str:
            src = tag.get('src', '#')
            file_name = os.path.basename(src)
            return f"[^{file_name}]"

    registry = StrategyRegistry()
    registry.register_all()  # register all tags
    registry.register("img", CustomImgConverter()) # override img tag

    converter = HtmlToJiraWikiConverter(registry)
    jira_wiki = converter.convert(html)

    return jira_wiki


if __name__ == "__main__":
    with open("templates/example_2.html") as fd:
        example = client(fd.read())
        print(example)
