#!/usr/bin/env python3
"""html_strip — Strip HTML tags, extract text, links, and metadata.

Usage:
    html_strip.py strip file.html
    html_strip.py links file.html
    html_strip.py meta file.html
    html_strip.py headings file.html
    curl -s "https://example.com" | html_strip.py strip -
"""

import sys
import re
import json
import argparse
from html.parser import HTMLParser
from html import unescape


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.links = []
        self.headings = []
        self.meta = {}
        self.title = ''
        self._tag_stack = []
        self._skip_tags = {'script', 'style', 'noscript', 'svg', 'head'}
        self._in_skip = 0
        self._current_heading = None
        self._heading_text = []
        self._in_title = False
        self._title_text = []
        self._current_link = None
        self._link_text = []

    def handle_starttag(self, tag, attrs):
        self._tag_stack.append(tag)
        attrs_dict = dict(attrs)

        if tag in self._skip_tags:
            self._in_skip += 1

        if tag == 'title':
            self._in_title = True
            self._title_text = []

        if tag == 'meta':
            name = attrs_dict.get('name', attrs_dict.get('property', ''))
            content = attrs_dict.get('content', '')
            if name and content:
                self.meta[name] = content

        if tag == 'a' and 'href' in attrs_dict:
            self._current_link = attrs_dict['href']
            self._link_text = []

        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            self._current_heading = tag
            self._heading_text = []

        if tag == 'br':
            self.text.append('\n')
        if tag in ('p', 'div', 'li', 'tr', 'blockquote', 'article', 'section'):
            self.text.append('\n')

    def handle_endtag(self, tag):
        if tag in self._skip_tags:
            self._in_skip = max(0, self._in_skip - 1)

        if tag == 'title':
            self._in_title = False
            self.title = ''.join(self._title_text).strip()

        if tag == 'a' and self._current_link is not None:
            text = ''.join(self._link_text).strip()
            self.links.append({'href': self._current_link, 'text': text})
            self._current_link = None

        if tag == self._current_heading:
            text = ''.join(self._heading_text).strip()
            level = int(tag[1])
            self.headings.append({'level': level, 'text': text})
            self._current_heading = None

        if tag in ('p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'tr'):
            self.text.append('\n')

        if self._tag_stack and self._tag_stack[-1] == tag:
            self._tag_stack.pop()

    def handle_data(self, data):
        if self._in_title:
            self._title_text.append(data)
        if self._current_link is not None:
            self._link_text.append(data)
        if self._current_heading:
            self._heading_text.append(data)
        if self._in_skip == 0:
            self.text.append(data)

    def handle_entityref(self, name):
        self.handle_data(unescape(f'&{name};'))

    def handle_charref(self, name):
        self.handle_data(unescape(f'&#{name};'))

    def get_text(self):
        raw = ''.join(self.text)
        # Collapse whitespace
        lines = raw.split('\n')
        cleaned = []
        for line in lines:
            line = ' '.join(line.split())
            cleaned.append(line)
        # Remove excessive blank lines
        result = []
        prev_blank = False
        for line in cleaned:
            if not line:
                if not prev_blank:
                    result.append('')
                prev_blank = True
            else:
                result.append(line)
                prev_blank = False
        return '\n'.join(result).strip()


def read_input(path):
    if path == '-':
        return sys.stdin.read()
    with open(path) as f:
        return f.read()


def cmd_strip(args):
    html = read_input(args.input)
    parser = TextExtractor()
    parser.feed(html)
    print(parser.get_text())


def cmd_links(args):
    html = read_input(args.input)
    parser = TextExtractor()
    parser.feed(html)

    if args.json:
        print(json.dumps(parser.links, indent=2))
    else:
        seen = set()
        for link in parser.links:
            href = link['href']
            if href in seen:
                continue
            seen.add(href)
            text = link['text']
            if text and text != href:
                print(f'  {text}: {href}')
            else:
                print(f'  {href}')


def cmd_meta(args):
    html = read_input(args.input)
    parser = TextExtractor()
    parser.feed(html)

    info = {'title': parser.title}
    info.update(parser.meta)

    if args.json:
        print(json.dumps(info, indent=2))
    else:
        for k, v in info.items():
            print(f'{k}: {v}')


def cmd_headings(args):
    html = read_input(args.input)
    parser = TextExtractor()
    parser.feed(html)

    for h in parser.headings:
        indent = '  ' * (h['level'] - 1)
        print(f'{indent}{"#" * h["level"]} {h["text"]}')


def main():
    p = argparse.ArgumentParser(description='HTML text extractor')
    p.add_argument('--json', action='store_true')
    sub = p.add_subparsers(dest='cmd', required=True)

    s = sub.add_parser('strip', help='Strip HTML, extract text')
    s.add_argument('input', nargs='?', default='-')
    s.set_defaults(func=cmd_strip)

    s = sub.add_parser('links', help='Extract all links')
    s.add_argument('input', nargs='?', default='-')
    s.set_defaults(func=cmd_links)

    s = sub.add_parser('meta', help='Extract metadata')
    s.add_argument('input', nargs='?', default='-')
    s.set_defaults(func=cmd_meta)

    s = sub.add_parser('headings', help='Extract heading structure')
    s.add_argument('input', nargs='?', default='-')
    s.set_defaults(func=cmd_headings)

    args = p.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
