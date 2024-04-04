import util
import output
from scrapper import Scrapper

if __name__ == "__main__":
    args = util.parse()

    if args["group"] and (args["note"] or args["frontnote"] or args["endnote"]):
        print("NOTE: Can't handle notes on multiple part chapters yet. Will display notes only for first chapter!")

    util.make_dir(args)
    scrapper = Scrapper(args)
    chapters = scrapper.run()

    if not args["batch"]:
        output.run_from_list(args, chapters)

