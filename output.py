import os
import re


def run(args, chapters):
    loc = os.path.join(args['output'], args['book_title'])
    epub = args['epub']

    if not epub:
        os.makedirs(loc, exist_ok=True)
        for chapter in chapters:
            i = str(chapter.index).zfill(4)

            sanitize = chapter.title[:35].strip()
            sanitize = re.sub(r"""["*\\/'’ .|?:<>%– ]""", "_", sanitize)

            name = "Chapter " + i + "_" + sanitize + ".html"
            file_loc = os.path.join(loc, name)
            with open(file_loc, 'wb') as f:
                f.write(str(chapter).encode("utf-8"))
            print(f"Wrote chapter {i}: {chapter.title}")

    elif epub:
        pass
