import os
import re
import shutil
from argparse import ArgumentParser as AP
from urllib.request import Request, urlopen

# import browser_cookie3
import requests


def make_dir(args):
    loc = os.path.join(args["output"], args["book_title"])
    os.makedirs(loc, exist_ok=True)
    if args["file"]:
        shutil.copyfile(os.path.expanduser("~/Templates/Epub file.epub"), loc + ".epub")


# Parse CLI arguments and return as a dictionary
def parse():
    parser = AP()
    parser.add_argument("url", help="URL of the first chapter")
    parser.add_argument(
        "-o",
        "--output",
        default=os.path.expanduser("~/Downloads/Serials"),
        help="Output location",
    )
    parser.add_argument("-t", "--book_title", default="", help="Book title")
    parser.add_argument(
        "-g", "--group", action="store_true", help="Heuristically merge split chapters"
    )
    parser.add_argument(
        "-n", "--note", action="store_true", help="Add Author's front and end notes"
    )
    parser.add_argument(
        "-fn", "--frontnote", action="store_true", help="Add Author's front notes"
    )
    parser.add_argument(
        "-en", "--endnote", action="store_true", help="Add Author's end notes"
    )
    parser.add_argument(
        "-toc",
        "--toc",
        action="store_true",
        help="Use a TOC file instead of first chapter's URL",
    )
    parser.add_argument(
        "-f", "--file", action="store_true", help="Create empty file from template"
    )
    parser.add_argument(
        "-b",
        "--batch",
        action="store_true",
        help="Write chapters in one batch instead of one-by-one",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Print more logs")
    parser.add_argument(
        "-i",
        "--index",
        default=1,
        help="First chapter's index",
    )

    args = vars(parser.parse_args())
    args["url"] = args["url"].strip()
    args["output"] = args["output"].strip()
    args["book_title"] = args["book_title"].strip()
    if args["note"]:
        args["endnote"] = True
        args["frontnote"] = True

    return args


# Scrap from URL and return HTML code
def scrap(url):
    # cj = browser_cookie3.firefox(domain_name="scribblehub.com")
    # html = requests.get(url, cookies=cj).content
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    html = urlopen(request).read()

    return html


# Checks if the text or class of a tag indicates it belongs to a relevant class
def in_list(type, tag):
    if type == "next":
        accepts = [
            "next chapter",
            "next",
            "next part",
            "next –>",
            "‹ previous",
        ]  # "previous" is for kemono
        text = tag.text

    elif type == "note":
        accepts = ["portlet-body author-note"]
        if not tag.has_attr("class") or len(tag["class"]) == 0:
            return False
        if len(tag["class"]) > 1:
            text = " ".join(tag["class"])
        else:
            text = tag["class"][0]

    elif type == "title":
        accepts = [
            "font-white break-word",
            "entry-title",
            "leader",
            "chapter-title",
            "post__title",
            "post-title",
            "pjgm-posttitle",
        ]
        if not tag.has_attr("class") or len(tag["class"]) == 0:
            return False
        if len(tag["class"]) > 1:
            text = " ".join(tag["class"])
        else:
            text = tag["class"][0]

    elif type == "content":
        accepts = [
            "chapter-inner chapter-content",
            "entry-content",
            "entry clear",
            "hentry",
            "chapter-content",
            "chp_raw",
            "post-content--padded",
            "post__content",
            "post text",
            "body entry-content",
            "entry-content clear",
            "pjgm-postcontent",
        ]
        if not tag.has_attr("class") or len(tag["class"]) == 0:
            return False
        if len(tag["class"]) > 1:
            text = " ".join(tag["class"])
        else:
            text = tag["class"][0]

    else:
        raise Exception("Wrong or missing type")

    for accept in accepts:
        if text.strip().lower() == accept:
            return True
    return False


# checks if the title indicates the chapter is part of a split
# Returns its index within the split
def get_part(title):
    title = title.lower()

    # .1:
    match = re.search(r".+\d+\.(\d+).*$", title)
    if match is not None:
        return int(match.group(1))

    # part 1 (of 2)...
    match = re.search(r".+\s\(?part\s(\d+)\)?(\sof\s\d+)?.*$", title)
    if match is not None:
        return int(match.group(1))

    # 1/2
    match = re.search(r".+\s(\d+)/\d+$", title)
    if match is not None:
        return int(match.group(1))

    # p1
    match = re.search(r".+\sp(\d+)$", title)
    if match is not None:
        return int(match.group(1))

    # Add more patterns as they are found
    # Note: Precision over Recall!

    return 1
