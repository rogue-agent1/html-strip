#!/usr/bin/env python3
"""html_strip - Strip HTML to plain text."""
import sys, argparse, json, re
from html.parser import HTMLParser

class Stripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.links = []
        self._tag = None
    def handle_starttag(self, tag, attrs):
        self._tag = tag
        if tag == "a":
            href = dict(attrs).get("href")
            if href: self.links.append(href)
        if tag in ("br", "p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li"):
            self.text.append("\n")
    def handle_data(self, data):
        self.text.append(data)
    def get_text(self):
        return re.sub(r"\n{3,}", "\n\n", "".join(self.text)).strip()

def main():
    p = argparse.ArgumentParser(description="HTML stripper")
    p.add_argument("input", help="HTML string or @filename")
    p.add_argument("--links", action="store_true", help="Extract links")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    html = args.input
    if html.startswith("@"):
        with open(html[1:]) as f: html = f.read()
    s = Stripper()
    s.feed(html)
    text = s.get_text()
    if args.json:
        result = {"text": text, "length": len(text), "html_length": len(html)}
        if args.links: result["links"] = s.links
        print(json.dumps(result, indent=2))
    else:
        print(text)
        if args.links:
            print("\nLinks:")
            for link in s.links: print(f"  {link}")

if __name__ == "__main__": main()
