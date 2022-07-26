import util
from chapter import Chapter
from bs4 import BeautifulSoup as Soup
from urllib.parse import urljoin


class Scrapper():
    def __init__(self, args):
        self.root = args['url']
        self.group = args['group']
        self.book_title = args['book_title']

    def run(self):
        next = self.root
        index = 1
        chapters = []

        while next:
            # Scrap HTML
            html = util.scrap(next)
            soup = Soup(html, "html.parser")
            
            # Find next chapter URL
            link = soup.find(lambda tag: tag.name == 'a' and util.in_list('next', tag))
            next = urljoin(next, link['href']) if link else None

            # Find chapter title
            title = soup.find(lambda tag: tag.name in ['h1', 'h2', 'h3'] and util.in_list('title', tag))
            title = title.text

            # Find authors note
            note = soup.find(lambda tag: tag.name == 'div' and util.in_list('note', tag))
            note = str(note)

            # Find chapter contents
            content = soup.find(lambda tag: tag.name == 'div' and util.in_list('content', tag))
            content = str(content)
            
            # Check if chapter part of split, merge if necessary
            part = util.get_part(title)
            if self.group and part != 1:
                assert len(chapters) >= 1
                chapters[-1].add_content(content)
                chapters[-1].merge_titles(title)
            
            else:
                chapter = Chapter(index, title, note, content, self.book_title)            
                chapters.append(chapter)

                print(f"Scanned chapter {index}: {title}")
                index += 1
        
        return chapters