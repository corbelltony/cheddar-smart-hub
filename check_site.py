"""Check this static site's HTML, links, assets, and public-file safety."""

from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urljoin, urlsplit
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent
BASE_URL = "https://corbelltony.github.io/cheddar-smart-hub/"
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
EXPECTED = {"index.html", "privacy.html", "styles.css", "favicon.svg", ".nojekyll", ".gitignore", "README.md", "check_site.py"}
FAILURES = []


def require(condition, message):
    if not condition:
        FAILURES.append(message)


class Document(HTMLParser):
    def __init__(self, name):
        super().__init__(convert_charrefs=True)
        self.name = name
        self.stack = []
        self.ids = set()
        self.links = []
        self.headings = 0
        self.title = False
        self.language = False
        self.charset = False
        self.viewport = False
        self.doctype = False
        self.main = False
        self.description = False

    def handle_decl(self, decl):
        self.doctype = decl.lower() == "doctype html"

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        require(tag not in {"script", "form", "iframe", "object", "embed", "input", "textarea"}, f"{self.name}: disallowed active/embedded content")
        require(not any(key.startswith("on") for key in attributes), f"{self.name}: inline event handler")
        require("style" not in attributes, f"{self.name}: styles must stay in the local stylesheet")
        if tag not in VOID:
            self.stack.append(tag)
        if "id" in attributes:
            require(attributes["id"] not in self.ids, f"{self.name}: duplicate element ID")
            self.ids.add(attributes["id"])
        if tag == "html":
            self.language = attributes.get("lang") == "en"
        if tag == "h1":
            self.headings += 1
        if tag == "title":
            self.title = True
        if tag == "main":
            self.main = True
        if tag == "meta":
            self.charset |= attributes.get("charset", "").lower() == "utf-8"
            self.viewport |= attributes.get("name") == "viewport" and "width=device-width" in attributes.get("content", "")
            self.description |= attributes.get("name") == "description" and bool(attributes.get("content"))
        for key in ("href", "src"):
            if key in attributes:
                url = attributes[key]
                self.links.append((tag, attributes.get("rel", ""), url))
                if tag != "a" and attributes.get("rel") != "canonical":
                    require(not urlsplit(url).scheme and not url.startswith("//"), f"{self.name}: external asset dependency")

    def handle_endtag(self, tag):
        require(bool(self.stack) and self.stack[-1] == tag, f"{self.name}: mismatched closing tag {tag}")
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()


documents = {}
for name in ("index.html", "privacy.html"):
    path = ROOT / name
    if not path.is_file():
        FAILURES.append(f"Missing page: {name}")
        continue
    document = Document(name)
    document.feed(path.read_text(encoding="utf-8"))
    document.close()
    require(not document.stack, f"{name}: unclosed HTML elements")
    require(all((document.doctype, document.language, document.charset, document.viewport, document.description, document.title, document.main)), f"{name}: missing document metadata or main landmark")
    require(document.headings == 1, f"{name}: expected one main heading")
    documents[name] = document

link_count = 0
for name, document in documents.items():
    for tag, relationship, url in document.links:
        link_count += 1
        parts = urlsplit(url)
        require(parts.scheme not in {"javascript", "data"}, f"{name}: unsafe URL scheme")
        if parts.scheme or parts.netloc:
            require(parts.scheme == "https", f"{name}: external links must use HTTPS")
            continue
        require(not parts.path.startswith("/"), f"{name}: root-relative URL breaks project hosting")
        target = (ROOT / (unquote(parts.path) or name)).resolve()
        require(target.is_relative_to(ROOT) and target.is_file(), f"{name}: missing or out-of-directory local target")
        hosted = urljoin(BASE_URL + name, url)
        require(hosted.startswith(BASE_URL), f"{name}: local URL leaves the GitHub project path")
        if parts.fragment:
            destination = documents.get(target.name)
            require(destination is not None and unquote(parts.fragment) in destination.ids, f"{name}: missing fragment target")

css = (ROOT / "styles.css").read_text(encoding="utf-8")
require(css.count("{") == css.count("}"), "styles.css: unbalanced rule braces")
require("@import" not in css.lower(), "styles.css: imported dependency")
require(not re.search(r"url\(\s*[\"']?(?:https?:|//|data:)", css, re.I), "styles.css: external asset")
require("@media" in css and ":focus-visible" in css, "styles.css: responsive or keyboard-focus styles missing")
try:
    ET.parse(ROOT / "favicon.svg")
except (ET.ParseError, OSError):
    FAILURES.append("favicon.svg: invalid SVG")
require((ROOT / ".nojekyll").is_file(), "Missing .nojekyll")

for path in ROOT.iterdir():
    if path.name in {".local-qa", "__pycache__", ".git"}:
        continue
    require(path.name in EXPECTED and path.is_file() and not path.is_symlink(), "Unexpected public file or directory; review before publishing")
    if path.name not in EXPECTED or not path.is_file():
        continue
    content = path.read_bytes()
    for pattern in (rb"AIza[0-9A-Za-z_-]{35}", rb"GOCSPX-[0-9A-Za-z_-]{20,}", rb"1//[0-9A-Za-z_-]{20,}",
                    rb"ya29\.[0-9A-Za-z_.-]{20,}", rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
                    rb"\b192\.168\.\d{1,3}\.\d{1,3}\b", rb"\b10\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
                    rb"\b172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}\b"):
        require(re.search(pattern, content) is None, f"{path.name}: possible sensitive material (value withheld)")

if FAILURES:
    for failure in FAILURES:
        print("FAIL: " + failure)
    sys.exit(1)
print(f"PASS: {len(documents)} HTML pages; {link_count} links/resources; local assets and project-path links valid.")
print("PASS: responsive/focus styles present; no scripts, forms, external asset dependencies, or detected sensitive material.")
