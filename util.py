import os
import re
from argparse import ArgumentParser as AP
from urllib.request import Request, urlopen


# Parse CLI arguments and return as a dictionary
def parse():
    parser = AP()
    parser.add_argument('url', help="URL of the first chapter")
    parser.add_argument('-o', '--output', default=os.path.expanduser('~/Downloads'), help="Output location")
    parser.add_argument('-t', '--book_title', default="", help="Book title")
    parser.add_argument('-e', "--epub", action='store_true', help="Compile serial into epub")
    parser.add_argument('-g', '--group', action='store_true', help='Heuristically merge split chapters')
    parser.add_argument('-n', '--note', action='store_true', help="Add Author's notes")

    args = vars(parser.parse_args())
    args['url'] = args['url'].strip()
    args['output'] = args['output'].strip()
    args['book_title'] = args['book_title'].strip()

    return args


# Scrap from URL and return HTML code
def scrap(url):
    request = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urlopen(request).read()

    return html


# Checks if the text or class of a tag indicates it belongs to a relevant class
def in_list(type, tag):
    if type == 'next':
        accepts = ["next chapter", "next"]
        text = tag.text

    elif type == 'note':
        accepts = ["portlet-body author-note"]
        if not tag.has_attr('class'):
            return False
        if len(tag['class']) > 1:
            text = " ".join(tag['class'])
        else:
            text = tag['class'][0]

    elif type == 'title':
        accepts = ["font-white", "entry-title"]
        if not tag.has_attr('class'):
            return False
        if len(tag['class']) > 1:
            text = " ".join(tag['class'])
        else:
            text = tag['class'][0]

    elif type == 'content':
        accepts = ["chapter-inner chapter-content", "entry-content"]
        if not tag.has_attr('class'):
            return False
        if len(tag['class']) > 1:
            text = " ".join(tag['class'])
        else:
            text = tag['class'][0]

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

    # 1/2
    match = re.search(r".+\s(\d+)/\d+$", title)
    if match is not None:
        return int(match.group(1))

    # part 1 (of 2)
    match = re.search(r".+\spart\s(\d+)(\sof\s\d+)?$", title)
    if match is not None:
        return int(match.group(1))

    # p1
    match = re.search(r".+\sp(\d+)$", title)
    if match is not None:
        return int(match.group(1))

    # Add more patterns as they are found
    # Note: Precision over Recall!

    return 1
