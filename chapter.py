from bs4 import BeautifulSoup as BS
import requests
import re
import os


class Chapter:
    def __init__(self, index, title, front_note, end_note, content, book_title, output_loc):
        self.index = index
        self.title = title
        self.front_note = front_note
        self.end_note = end_note
        self.content = content
        self.book_title = book_title
        self.output_loc = os.path.join(output_loc, book_title)
        self.filter_content()

    def filter_content(self):
        for i, html in enumerate([self.front_note, self.end_note, self.content]):
            soup = BS(html, "html.parser")

            # Unwrap divs and spans
            for tag in soup.find_all(["span", "div"]):
                tag.unwrap()

            # Remove scripts and their content
            for tag in soup.find_all(["script"]):
                tag.decompose()

            # Standardize and replace tag names
            for old, new in [("strong", "b"), ("i", "em"), ("cite", "p")]:
                for tag in soup.find_all(old):
                    tag.name = new

            # Download image and replace urls with local files
            for tag in soup.find_all(["img"]):
                img_href = tag["src"]
                img_data = requests.get(img_href).content
                img_title = re.sub(r"""["*\\/'’ .|?:<>&%– ]""", "", img_href)[:40].strip() + ".jpg"
                with open(os.path.join(self.output_loc, img_title), "wb") as handler:
                    handler.write(img_data)
                tag["src"] = "../Images/" + img_title
                for attr in dict(tag.attrs):
                    if attr not in ["src", "alt", "style", "height", "width"]:
                        del tag.attrs[attr]

            html = str(soup)
            if i == 0:
                self.front_note = html
            elif i == 1:
                self.end_note = html
            elif i == 2:
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
        prefix = (
                """<?xml version="1.0" encoding="utf-8"?>
                    <!DOCTYPE html>
                        <html>
                        <head>
            <meta content="text/html; charset=UTF-8" http-equiv="default-style"/>
                          <title>"""
                + self.book_title
                + """</title>
        <link href="../Styles/stylesheet.css" rel="stylesheet" type="text/css"/>
                    </head>
                    <body lang="en">
                      """
        )
        header = (
                "<h2>"
                + self.title
                + """</h2>
                    <img alt="Decoration" src="../Images/ornaments_1.jpg"/>
                    """
        )
        suffix = "</body></html>"

        front_note = "<h3>Author's note:</h3>" + self.front_note + "<hr/>"
        end_note = "<h3>Author's note:</h3>" + self.end_note + "<hr/>"

        if str(self.front_note) != "None" and str(self.end_note) != "None":
            return prefix + header + front_note + self.content + end_note + suffix
        if str(self.front_note) != "None" and str(self.end_note) == "None":
            return prefix + header + front_note + self.content + suffix
        if str(self.front_note) == "None" and str(self.end_note) != "None":
            return prefix + header + self.content + end_note + suffix
        return prefix + header + self.content + suffix
