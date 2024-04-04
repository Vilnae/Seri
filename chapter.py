from bs4 import BeautifulSoup as BS
from urllib.parse import urlparse
import requests
import re
import os

spam_list = [
            "Stolen from Royal Road, this story should be reported if encountered on Amazon.",
            "Stolen from its original source, this story is not meant to be on Amazon; report any sightings.",
            "A case of theft: this story is not rightfully on Amazon; if you spot it, report the violation.",
            "This tale has been pilfered from Royal Road. If found on Amazon, kindly file a report.",
            "The narrative has been stolen; if detected on Amazon, report the infringement.",
            "The story has been illicitly taken; should you find it on Amazon, report the infringement.",
            "If you come across this story on Amazon, be aware that it has been stolen from Royal Road. Please report it.",
            "Royal Road's content has been misappropriated; report any instances of this story if found elsewhere.",
            "Unauthorized use of content: if you find this story on Amazon, report the violation.",
            "The author's content has been appropriated; report any instances of this story on Amazon.",
            "Stolen novel; please report.",
            "The story has been taken without consent; if you see it on Amazon, report the incident.",
            "This story has been stolen from Royal Road. If you read it on Amazon, please report it",
            "If you encounter this story on Amazon, note that it's taken without permission from the author. Report it.",
            "If you come across this story on Amazon, it's taken without permission from the author. Report it.",
            "If you spot this story on Amazon, know that it has been stolen. Report the violation.",
            "This narrative has been purloined without the author's approval. Report any appearances on Amazon.",
            "Unauthorized use: this story is on Amazon without permission from the author. Report any sightings.",
            "The narrative has been taken without permission. Report any sightings.",
            "Stolen content alert: this content belongs on Royal Road. Report any occurrences.",
            "If you find this story on Amazon, be aware that it has been stolen. Please report the infringement.",
            "Unauthorized reproduction: this story has been taken without approval. Report sightings.",
            "Unauthorized content usage: if you discover this narrative on Amazon, report the violation.",
            "Unauthorized duplication: this narrative has been taken without consent. Report sightings.",
            "The tale has been taken without authorization; if you see it on Amazon, report the incident.",
            "The narrative has been illicitly obtained; should you discover it on Amazon, report the violation.",
            "A case of literary theft: this tale is not rightfully on Amazon; if you see it, report the violation.",
            "Unauthorized usage: this narrative is on Amazon without the author's consent. Report any sightings.",
            "Stolen from its rightful place, this narrative is not meant to be on Amazon; report any sightings."
            ]

class Chapter:
    def __init__(self, index, title, front_note, end_note, content, book_title, output_loc, url):
        self.index = index
        self.title = title
        self.front_note = front_note
        self.end_note = end_note
        self.content = content
        self.book_title = book_title
        self.output_loc = os.path.join(output_loc, book_title)
        self.url = url
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

            # Remove RoyalRoad spam
            for tag in soup.find_all(lambda tag: tag.text in spam_list):
                tag.decompose()

            for tag in soup.find_all("p", {"display": "none"}):
                tag.decompose()

            # Standardize and replace tag names
            for old, new in [("strong", "b"), ("i", "em"), ("cite", "p")]:
                for tag in soup.find_all(old):
                    tag.name = new

            # Download image and replace urls with local files
            for tag in soup.find_all(["img"]):
                if "src" not in tag.attrs:
                    continue
                img_href = tag["src"]
                if not str(img_href).startswith("../Images/"):
                    if img_href.startswith("/"):
                        parsed = urlparse(self.url)
                        img_href = f"{parsed.scheme}://{parsed.netloc}{img_href}"
                    # TODO: Optimize this:
                    img_title = re.sub(r"""["*\\/'’ .|?:<>&%– ]""", "", img_href)[:127].strip() + ".jpg"
                    img_title = re.sub('jpg\.jpg$', '.jpg', img_title)
                    img_title = re.sub('png\.jpg$', '.png', img_title)
                    img_path = os.path.join(self.output_loc, img_title)
                    if not os.path.exists(img_path):
                        img_data = requests.get(img_href).content
                        with open(img_path, "wb") as handler:
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
        end_note = "<hr/><h3>Author's note:</h3>" + self.end_note

        if str(self.front_note) != "None" and str(self.end_note) != "None":
            return prefix + header + front_note + self.content + end_note + suffix
        if str(self.front_note) != "None" and str(self.end_note) == "None":
            return prefix + header + front_note + self.content + suffix
        if str(self.front_note) == "None" and str(self.end_note) != "None":
            return prefix + header + self.content + end_note + suffix
        return prefix + header + self.content + suffix
