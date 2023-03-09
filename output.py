import os
import re
import zipfile


def run(args, chapters):
    loc = os.path.join(args["output"], args["book_title"])
    epub = args["epub"]

    if epub:
        file_name = loc + ".epub"
        epub = zipfile.ZipFile(file_name, "w")
        epub.writestr("mimetype", "application/epub+zip")
        epub.writestr(
            "META-INF/container.xml",
            """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>""",
        )
        index_tpl = """<package version="3.0" unique-identifier="BookId" prefix="calibre: https://calibre-ebook.com" xmlns="http://www.idpf.org/2007/opf">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
    <meta content="1.9.20" name="Sigil version"/>
  <metadata/>
  <manifest>
    %(manifest)s
  </manifest>
  <spine>
    %(spine)s
  </spine>
</package>"""
        manifest = """    <item id="nav.xhtml" href="Text/nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="sgc-nav.css" href="Styles/sgc-nav.css" media-type="text/css"/>
    <item id="stylesheet.css" href="Styles/stylesheet.css" media-type="text/css"/>
    <item id="ornaments_1.jpg" href="Images/ornaments_1.jpg" media-type="image/jpeg"/>
    <item id="ACaslonPro-Regular.otf" href="Fonts/ACaslonPro-Regular.otf" media-type="font/otf"/>
    <item id="Bookerly-Bold.ttf" href="Fonts/Bookerly-Bold.ttf" media-type="font/ttf"/>
    <item id="Bookerly-BoldItalic.ttf" href="Fonts/Bookerly-BoldItalic.ttf" media-type="font/ttf"/>
    <item id="Bookerly-Regular.ttf" href="Fonts/Bookerly-Regular.ttf" media-type="font/ttf"/>
    <item id="Bookerly-RegularItalic.ttf" href="Fonts/Bookerly-RegularItalic.ttf" media-type="font/ttf"/>
    <item id="Title0001.xhtml" href="Text/Title0001.xhtml" media-type="application/xhtml+xml"/>
    <item id="ornaments_2.jpg" href="Images/ornaments_2.jpg" media-type="image/jpeg"/>
    <item id="block_1.png" href="Images/block_1.png" media-type="image/png"/>
    <item id="block_2.png" href="Images/block_2.png" media-type="image/png"/>"""
        spine = """    <itemref idref="nav.xhtml" linear="no"/>
    <itemref idref="Title0001.xhtml"/>"""
        epub.write("OEBPS/Text/")

    for chapter in chapters:
        i = str(chapter.index).zfill(4)

        sanitize = chapter.title[:35].strip()
        sanitize = re.sub(r"[^a-zA-Z0-9-_+=\(\) ,]", "_", sanitize)
        # sanitize = re.sub(r"""["*\\/'’ .|?:<>%– ]""", "_", sanitize)

        name = "Chapter " + i + "_" + sanitize + ".html"
        file_loc = os.path.join(loc, name)
        if not epub:
            with open(file_loc, "wb") as f:
                f.write(str(chapter).encode("utf-8"))
            print(f"Wrote chapter {i}: {chapter.title}")
        elif epub:
            manifest += (
                '<item id="{}" href="{}" media-type="application/xhtml+xml"/>'.format(
                    name, "Text/" + name
                )
            )
            spine += '<itemref idref="{}"/>'.format(name)
            epub.write("OEBPS/Text/" + name, str(chapter).encode("utf-8"))
            print(f"Wrote chapter {i}: {chapter.title}")

    if epub:
        epub.writestr(
            "OEBPS/Content.opf",
            index_tpl
            % {
                "manifest": manifest,
                "spine": spine,
            },
        )
