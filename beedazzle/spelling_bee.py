"""Script for solving NYT's Spelling Bee game"""
import sys
from beedazzle.trie import Trie

MINIMUM_SCORE = -2


class DoesNotExistError(Exception):
    """"""
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def main():
    """Main function for script"""
    json_filename = "beedazzle/data/words.json"
    trie = Trie()
    trie.import_from_json_file(json_filename)
    if trie.is_empty():
        trie.import_from_txt_file("beedazzle/data/words_alpha.txt")

    letters = list(sys.argv[1])

    if len(letters) != 7:
        print("Invalid number of letters submitted")
        return

    trie.play(letters)
    # trie.retrospective(letters)

    trie.export_to_json_file(json_filename)


if __name__ == "__main__":
    main()
