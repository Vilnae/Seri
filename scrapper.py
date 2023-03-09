import util
from chapter import Chapter
from bs4 import BeautifulSoup as Soup
from urllib.parse import urljoin


class Scrapper:
    def __init__(self, args):
        self.root = args["url"]
        self.group = args["group"]
        self.book_title = args["book_title"]
        self.output_loc = args["output"]
        # self.add_note = args["note"]
        self.add_front_note = args["frontnote"]
        self.add_end_note = args["endnote"]
        if args["note"]:
            self.add_end_note = True
            self.add_front_note = True

    def run(self):
        next = self.root
        index = 1
        chapters = []

        while next:
            # Scrap HTML
            html = util.scrap(next)
            soup = Soup(html, "html.parser")

            # Find next chapter URL
            link = soup.find(lambda tag: tag.name == "a" and util.in_list("next", tag))
            link = link if (link and link["href"] != "#") else None
            next = urljoin(next, link["href"]) if link else None

            # Find chapter title
            title = soup.find(
                lambda tag: tag.name in ["h1", "h2", "h3", "div"]
                and util.in_list("title", tag)
            )
            title = title.text

            # # Find authors note
            # # FIXME: Handle multiple notes (pre-chapter and post-chapter)
            # note = None
            # if self.add_note:
            #     note = soup.find(
            #         lambda tag: tag.name == "div" and util.in_list("note", tag)
            #     )
            # note = str(note)
            #
            # # Find chapter contents
            # content = soup.find(
            #     lambda tag: tag.name == "div" and util.in_list("content", tag)
            # )
            # content = str(content)

            front_note = None
            end_note = None
            content = None

            content_and_notes = soup.find_all(
                    lambda tag: tag.name == "div" and (util.in_list("note", tag) or util.in_list("content", tag))
            )

            for tag in content_and_notes:
                if util.in_list("note", tag):
                    if content is None and self.add_front_note:
                        front_note = tag
                    if content is not None and self.add_end_note:
                        end_note = tag
                else:
                    content = str(tag)
            front_note = str(front_note)
            end_note = str(end_note)

            # Check if chapter part of split, merge if necessary
            # TODO: handle notes on multiple parts
            part = util.get_part(title)
            if self.group and part != 1:
                assert len(chapters) >= 1
                chapters[-1].add_content(content)
                chapters[-1].merge_titles(title)

            else:
                chapter = Chapter(
                    index, title, front_note, end_note, content, self.book_title, self.output_loc
                )
                chapters.append(chapter)

                print(f"Scanned chapter {index}: {title}")
                index += 1

        return chapters
