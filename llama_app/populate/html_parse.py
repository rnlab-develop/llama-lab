from html.parser import HTMLParser


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []

    def handle_data(self, data):
        self.text.append(data)

    def get_text(self):
        return "".join(self.text)


def clean_html(html_string):
    parser = TextExtractor()
    parser.feed(html_string)
    text = parser.get_text()
    # Collapse any sequence of whitespace into a single space.
    clean_text = " ".join(text.split())
    return clean_text
