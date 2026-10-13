"""Check publication boundaries, generated coverage and local links."""
from html.parser import HTMLParser
from pathlib import Path
import json
import re
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.links = []
        self.answers = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag in ('a', 'link') and 'href' in attrs:
            self.links.append(attrs['href'])
        if tag in ('script', 'img') and 'src' in attrs:
            self.links.append(attrs['src'])
        if tag == 'details' and 'answer' in attrs.get('class', '').split():
            self.answers += 1


def main():
    data = json.loads((ROOT / 'content/faqs.json').read_text(encoding='utf-8'))
    html = (DOCS / 'index.html').read_text(encoding='utf-8')
    page = Page()
    page.feed(html)
    assert page.answers == len(data['faqs'])
    assert len(page.ids) == len(set(page.ids)), 'Duplicate DOM ID.'
    for faq in data['faqs']:
        assert 'faq-' + faq['id'] in page.ids
    anchors = set(page.ids) | {'category-' + c['id'] for c in data['categories']}
    for link in page.links:
        url = urlsplit(link)
        if url.scheme:
            assert url.scheme == 'https', 'Unsupported published link scheme: ' + link
            continue
        if url.path:
            path = (DOCS / unquote(url.path)).resolve()
            assert path.is_relative_to(DOCS.resolve()) and path.is_file(), 'Missing local asset: ' + link
        elif url.fragment:
            assert url.fragment in anchors, 'Missing local anchor: ' + link
    for path in DOCS.rglob('*'):
        if path.is_file() and path.suffix in ('.html', '.js', '.css', '.txt', '.json'):
            value = path.read_text(encoding='utf-8')
            assert not re.search(r'(?:[A-Za-z]:[\\/](?:Users|Programs|Modding))|file:///|\.codex|SOURCES-AND-CORRECTIONS|THREAD LINK NEEDED|@@[A-Z_]+@@', value), 'Private or unfinished content: ' + str(path)
    assert (DOCS / '.nojekyll').is_file()
    assert (DOCS / 'assets/site.js').read_bytes() == (ROOT / 'assets/site.js').read_bytes()
    assert (DOCS / 'assets/site.css').read_bytes() == (ROOT / 'assets/site.css').read_bytes()
    print(f'PASS: {page.answers} public answers; {len(page.links)} links/assets; no private authoring data or unfinished placeholders.')


if __name__ == '__main__':
    main()
