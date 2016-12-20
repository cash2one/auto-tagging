import re
class HtmlParser:
    patterns = {
    'short_comment':(r"<div class=\"comment\">.*?<span "
            r"class=\"votes pr5\">(.*?)</span>.*?<span class=\"allstar(\d+) "
            r"rating\" title=\".*?\"></span>.*?<p class=\"\">"
            r"([^<\n]+).*?\s*</p>\s+</div>")
            }
    def __init__(self, content_type = 'short_comment'):
        self.content_type = content_type

    def parse_content(self, html):
        #pattern = re.compile(self.patterns[self.content_type])
        #records = pattern.findall(html)
        records = re.findall(self.patterns[self.content_type], html, re.S)
        return records

