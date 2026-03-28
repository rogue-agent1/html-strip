#!/usr/bin/env python3
"""html_strip - Strip HTML tags and extract text."""
import sys,re
def strip_tags(html):
    html=re.sub(r"<script[^>]*>.*?</script>","",html,flags=re.DOTALL|re.IGNORECASE)
    html=re.sub(r"<style[^>]*>.*?</style>","",html,flags=re.DOTALL|re.IGNORECASE)
    html=re.sub(r"<!--.*?-->","",html,flags=re.DOTALL)
    html=re.sub(r"<br\s*/?>","\n",html,flags=re.IGNORECASE)
    html=re.sub(r"</(p|div|h[1-6]|li|tr)>","\n",html,flags=re.IGNORECASE)
    html=re.sub(r"<[^>]+>","",html)
    html=re.sub(r"&amp;","&",html);html=re.sub(r"&lt;","<",html);html=re.sub(r"&gt;",">",html)
    html=re.sub(r"&nbsp;"," ",html);html=re.sub(r"&quot;",'"',html);html=re.sub(r"&#(\d+);",lambda m:chr(int(m[1])),html)
    return re.sub(r"\n{3,}","\n\n",html).strip()
def extract_links(html):
    return re.findall(r'href=["']([^"']+)["']',html)
def extract_title(html):
    m=re.search(r"<title[^>]*>(.*?)</title>",html,re.DOTALL|re.IGNORECASE)
    return m[1].strip() if m else None
if __name__=="__main__":
    if len(sys.argv)<2:html=sys.stdin.read()
    else:html=open(sys.argv[1]).read()
    if "--links" in sys.argv:
        for l in extract_links(html):print(l)
    elif "--title" in sys.argv:print(extract_title(html) or"(no title)")
    else:print(strip_tags(html))
