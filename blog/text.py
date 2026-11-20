"""Safe formatting for post bodies.

Authors write plain text. A small, predictable subset is supported:
blank line -> new paragraph, ``## Heading``, ```fenced code``` and `inline code`.
Everything is HTML-escaped first, so user input can never inject markup.
"""
import re

from django.utils.html import escape
from markupsafe import Markup

FENCE_RE = re.compile(r'```([\w+-]*)[ \t]*\n(.*?)```', re.DOTALL)
INLINE_CODE_RE = re.compile(r'`([^`\n]+)`')
WORDS_PER_MINUTE = 200


def _render_prose(chunk):
    html = []
    for block in re.split(r'\n\s*\n', chunk.strip()):
        if not block.strip():
            continue
        text = INLINE_CODE_RE.sub(r'<code>\1</code>', escape(block.strip()))
        if text.startswith('## '):
            html.append(f'<h2>{text[3:]}</h2>')
        else:
            html.append(f'<p>{text.replace(chr(10), "<br>")}</p>')
    return ''.join(html)


def render_body(text):
    text = (text or '').replace('\r\n', '\n')
    html, pos = [], 0
    for match in FENCE_RE.finditer(text):
        html.append(_render_prose(text[pos:match.start()]))
        lang = match.group(1)
        label = f' data-lang="{escape(lang)}"' if lang else ''
        html.append(f'<pre{label}><code>{escape(match.group(2).rstrip())}</code></pre>')
        pos = match.end()
    html.append(_render_prose(text[pos:]))
    return Markup(''.join(html))


def plain_excerpt(text, words=28):
    """Excerpt without code blocks and markup symbols, for cards."""
    text = FENCE_RE.sub(' ', text or '')
    text = re.sub(r'^##.*$', ' ', text, flags=re.MULTILINE)
    text = text.replace('`', '')
    parts = text.split()
    excerpt = ' '.join(parts[:words])
    return excerpt + ('…' if len(parts) > words else '')


def reading_minutes(text):
    return max(1, round(len((text or '').split()) / WORDS_PER_MINUTE))
