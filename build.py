"""Build the public FAQ site with Python 3.10+; no external packages required."""
from pathlib import Path
from datetime import date
import html
import json
import re
import shutil

ROOT = Path(__file__).resolve().parent


def escape(value):
    return html.escape(str(value), quote=True)


def inline(text):
    slots = []

    def protect(match):
        code, label, url = match.groups()
        rendered = '<code>' + escape(code) + '</code>' if code is not None else (
            '<a href="' + escape(url) + '" target="_blank" rel="noopener noreferrer">' + escape(label) + '</a>')
        slots.append(rendered)
        return '\x01' + str(len(slots) - 1) + '\x02'

    value = re.sub(r'`([^`]+)`|\[([^\]]+)\]\((https://[^\s)]+)\)', protect, text)
    value = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', escape(value))
    value = re.sub(r'\x01(\d+)\x02', lambda m: slots[int(m[1])], value)
    return value


def markdown(text):
    result, paragraph, items = [], [], []
    kind = ''

    def flush_paragraph():
        if paragraph:
            result.append('<p>' + '<br>'.join(inline(line) for line in paragraph) + '</p>')
            paragraph.clear()

    def flush_list():
        if items:
            result.append('<' + kind + '>' + ''.join('<li>' + inline(line) + '</li>' for line in items) + '</' + kind + '>')
            items.clear()

    for line in text.splitlines():
        numbered = re.match(r'^\s*\d+\.\s*(.*)$', line)
        bullet = re.match(r'^\s*[-•]\s+(.+)$', line)
        if not line.strip():
            flush_paragraph()
            flush_list()
        elif numbered or bullet:
            flush_paragraph()
            next_kind = 'ol' if numbered else 'ul'
            if kind != next_kind:
                flush_list()
            kind = next_kind
            items.append((numbered or bullet).group(1))
        else:
            flush_list()
            paragraph.append(line)
    flush_paragraph()
    flush_list()
    return ''.join(result)


def build():
    data = json.loads((ROOT / 'content/faqs.json').read_text(encoding='utf-8'))
    allowed = {'id', 'category', 'title', 'body'}
    categories = {c['id']: c for c in data['categories']}
    ids = set()
    for row in data['faqs']:
        assert set(row) == allowed, 'Public answer fields must match the documented schema.'
        assert re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', row['id']) and row['id'] not in ids
        ids.add(row['id'])
        assert row['category'] in categories
        assert row['title'].strip() and row['body'].strip()
        assert not re.search(r'(?:^|[\s`(])[A-Za-z]:[\\/]|file://|https?://(?:localhost|127\.0\.0\.1)|THREAD LINK NEEDED', row['body'])

    category_buttons = '<button class="category-button" type="button" data-category="all" aria-pressed="true"><span class="icon" aria-hidden="true">▦</span><span>All answers</span><span class="count">' + str(len(ids)) + '</span></button>'
    for c in categories.values():
        count = sum(r['category'] == c['id'] for r in data['faqs'])
        category_buttons += f'<button class="category-button" type="button" data-category="{escape(c["id"])}" aria-pressed="false"><span class="icon" aria-hidden="true">{escape(c["icon"])}</span><span>{escape(c["title"])}</span><span class="count">{count}</span></button>'

    answers = []
    for number, row in enumerate(data['faqs'], 1):
        key = escape(row['id'])
        opened = ' open' if number == 1 else ''
        answers.append(f'''<details class="answer" id="faq-{key}" data-category="{escape(row['category'])}"{opened}>
<summary><span class="question-index" aria-hidden="true">{number:02d}</span><h3 class="question-heading">{escape(row['title'])}</h3></summary>
<div class="answer-content"><span class="answer-category">{escape(categories[row['category']]['title'])}</span><div class="markdown">{markdown(row['body'])}</div>
</div></details>''')

    updated = date.fromisoformat(data['updatedAt'])
    template = (ROOT / 'site.template.html').read_text(encoding='utf-8')
    report = (ROOT / 'content/bug-report-template.txt').read_text(encoding='utf-8')
    replacements = {
        '@@ANSWERS@@': '\n'.join(answers), '@@CATEGORIES@@': category_buttons,
        '@@ANSWER_COUNT@@': str(len(ids)), '@@CATEGORY_COUNT@@': str(len(categories)),
        '@@UPDATED@@': f'{updated.day} {updated.strftime("%B %Y")}',
        '@@REPORT@@': escape(report), '@@CANONICAL@@': escape(data['siteUrl']),
        '@@DATA@@': json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c'),
    }
    for key, value in replacements.items():
        template = template.replace(key, value)
    assert not re.search(r'@@[A-Z_]+@@', template), 'Unfilled template token.'
    output = ROOT / 'docs'
    (output / 'assets').mkdir(parents=True, exist_ok=True)
    (output / 'index.html').write_text(template, encoding='utf-8')
    (output / '.nojekyll').write_text('', encoding='utf-8')
    (output / 'bug-report-template.txt').write_text(report, encoding='utf-8')
    (output / 'faq.txt').write_text('\n\n'.join('## ' + r['title'] + '\n\n' + r['body'] for r in data['faqs']) + '\n', encoding='utf-8')
    for name in ('site.css', 'site.js', 'faq-banner.png', 'favicon.svg'):
        shutil.copy2(ROOT / 'assets' / name, output / 'assets' / name)
    print(f'Built {len(ids)} answers in {len(categories)} categories -> docs/index.html')


if __name__ == '__main__':
    build()
