# html_strip

Strip HTML tags, extract text, links, headings, and metadata.

## Usage

```bash
# Extract plain text from HTML
python3 html_strip.py strip page.html
curl -s "https://example.com" | python3 html_strip.py strip -

# Extract all links
python3 html_strip.py links page.html

# Extract metadata (title, description, og tags)
python3 html_strip.py meta page.html

# Extract heading structure
python3 html_strip.py headings page.html
```

## Features
- Clean text extraction (strips scripts, styles, SVG)
- Whitespace normalization
- Link extraction with anchor text
- Heading hierarchy
- Meta tag extraction (name, property, og:*)

## Zero dependencies. Single file. Python 3.8+.
