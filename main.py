import util
import output
from scrapper import Scrapper

if __name__ == "__main__":
    args = util.parse()

    scrapper = Scrapper(args)
    chapters = scrapper.run()
    output.run(args, chapters)
