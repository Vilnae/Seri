from bs4 import BeautifulSoup as BS


class Chapter:
    def __init__(self, index, title, note, content, book_title):
        self.index = index
        self.title = title
        self.note = note
        self.content = content
        self.book_title = book_title

        self.filter_content()

    def filter_content(self):
        for i, html in enumerate([self.note, self.content]):
            soup = BS(html, "html.parser")

            # Unwrap divs and spans
            for tag in soup.find_all(["span", "div"]):
                tag.unwrap()

            # Remove scripts and their content
            for tag in soup.find_all(["script"]):
                tag.decompose()

            # Standardize and replace tag names
            for old, new in [('strong', 'b'), ('i', 'em'), ('cite', 'p')]:
                for tag in soup.find_all(old):
                    tag.name = new

            html = str(soup)
            if i == 0:
                self.note = html
            elif i == 1:
                self.content = html

    # Add new content to current one
    def add_content(self, content):
        self.content += "<hr/>" + content
        self.filter_content()

    # Updates title to the equal substring at the beginning of current and new title
    def merge_titles(self, title):
        title1 = self.title
        title2 = title

        for i in range(min(len(title1), len(title2))):
            if title1[i] != title2[i]:
                self.title = title1[:i]
                break

    def __str__(self):
        prefix = """<?xml version="1.0" encoding="utf-8"?>
                <!DOCTYPE html>
                    <html>
                    <head>
                      <meta content="text/html; charset=UTF-8" http-equiv="default-style"/>
                      <title>""" + self.book_title + """</title>
                      <link href="../Styles/stylesheet.css" rel="stylesheet" type="text/css"/>
                    </head>
                    <body lang="en">
                      """
        header = "<h2>" + self.title + """</h2>        
                    <img alt="Decoration" src="../Images/ornaments_1.jpg"/>
                    """
        suffix = "</body></html>"

        note = "<h3>Author's note:</h3>" + self.note + "<hr/>"

        if str(self.note) != "None":
            return prefix + header + note + self.content + suffix
        return prefix + header + self.content + suffix
