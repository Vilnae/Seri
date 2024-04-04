import util
import output
from chapter import Chapter
from bs4 import BeautifulSoup as Soup
from urllib.parse import urljoin
from time import time
from datetime import timedelta


class Scrapper:
    def __init__(self, args):
        self.args = args

    def run(self):
        start_time = time()
        if self.args["toc"]:
            with open(self.args["url"], 'r') as f:
                links = [link.strip() for link in f.readlines() if link.strip() != ""]
            next = links.pop(0)
        else:
            next = self.args["url"]
        index = int(self.args["index"])
        chapters = []

        while next:
            # Scrap HTML
            html = util.scrap(next)
            soup = Soup(html, "html.parser")
            curr = next

            # Find next chapter URL
            if self.args["toc"]:
                next = links.pop(0) if len(links) != 0 else None
            else:
                link = soup.find(lambda tag: tag.name == "a" and util.in_list("next", tag))
                link = link if (link and link["href"] != "#") else None
                next = urljoin(next, link["href"]) if link else None

            # Find chapter title
            title = soup.find(
                lambda tag: tag.name in ["h1", "h2", "h3", "div"]
                and util.in_list("title", tag)
            )
            if title is not None and title.get_text():  # title.has_attr("text"):
                title = title.get_text()
            else:
                title = " "

            # Find author's notes and chapter content
            front_note = None
            end_note = None
            content = None

            content_and_notes = soup.find_all(
                    lambda tag: tag.name in ["div", "article"] and (util.in_list("note", tag) or util.in_list("content", tag))
            )

            for tag in content_and_notes:
                if util.in_list("note", tag):
                    if content is None and self.args["frontnote"]:
                        front_note = tag
                    if content is not None and self.args["endnote"]:
                        end_note = tag
                else:
                    content = str(tag)
            front_note = str(front_note)
            end_note = str(end_note)

            # Check if chapter part of split, merge if necessary
            # TODO: handle notes on multiple parts
            part = util.get_part(title)
            if self.args["group"] and part != 1:
                assert len(chapters) >= 1
                chapters[-1].add_content(content)
                chapters[-1].merge_titles(title)

            else:
                chapter = Chapter(
                    index, title, front_note, end_note, content, self.args["book_title"], self.args["output"], curr
                )
                chapters.append(chapter)

                dtime = timedelta(seconds=time() - start_time)
                dtime -= timedelta(microseconds=dtime.microseconds)
                print(f"[{dtime}] Scanned chapter {index}: {title.strip()}")
                index += 1

                if not self.args["batch"]:
                    output.run(self.args, chapter)

        return chapters
