import os
import re
import zipfile

def run(args, chapter):
    i = str(chapter.index).zfill(4)

    sanitized = chapter.title[:35].strip()
    sanitized = re.sub(r"[^a-zA-Z0-9-_+=\(\) ,]", "-", sanitized)
    sanitized = re.sub(r"--+", "-", sanitized)
    name = i + "_" + sanitized + ".html"
    file_loc = os.path.join(args["output"], args["book_title"], name)

    with open(file_loc, "wb") as f:
        f.write(str(chapter).encode("utf-8"))

    if args["verbose"]:
        print(f"Wrote {file_loc}")


def run_from_list(args, chapters):
    for chapter in chapters:
        run(args, chapter)
