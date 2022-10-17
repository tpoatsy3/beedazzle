import json

MINIMUM_SCORE = -2


class DoesNotExistError(Exception):
    """"""
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class Node:
    root = False
    children = {}
    symbol = None

    def __str__(self) -> str:
        return self.symbol

    def __init__(self,
                 symbol: str,
                 root: bool = False,
                 score: int = 0) -> None:
        if root:
            self.root = True
        else:
            self.root = False
            if symbol is None:
                self.symbol = "*"
            else:
                self.symbol = symbol.lower()
        self.children = {}
        self.score = score

    def add(self, input_str: str, score: int = 0):
        """Processes word into trie nodes"""
        if input_str == "":
            self.children["*"] = None
            self.score = score
            return
        char = input_str[0]
        next_node = self.children.get(char)
        if not next_node:
            next_node = Node(char)
            self.children[char] = next_node
        next_node.add(input_str[1:])

    def check(self, input_str):
        """Checks if input_str is in trie"""
        if input_str == "":
            if "*" in self.children:
                return self.score
            else:
                return False
        char = input_str[0]
        next_node = self.children.get(char)

        if not next_node:
            return False
        else:
            return next_node.check(input_str[1:])

    def adjust_word_score(self, stem, adjustment):
        """Adjust the score for an entry"""
        if stem == "":
            self.score += adjustment
            return
        char = stem[0]
        next_node = self.children.get(char)

        if not next_node:
            raise DoesNotExistError()
        else:
            return next_node.adjust_word_score(stem[1:], adjustment)

    def dump(self, stem):
        """Returns full content of input string"""
        found_words = []
        for char, node in self.children.items():
            if char == "*":
                found_words.append(stem)
                continue
            else:
                child_words = node.dump(stem + char)
                for child_word in child_words:
                    found_words.append(child_word)

        return found_words

    def export(self, stem):
        """Returns a dictionary of all words in the branch and their scores"""
        found_words = {}
        for char, node in self.children.items():
            if char == "*":
                if self.score >= MINIMUM_SCORE:
                    found_words[stem] = self.score
                continue
            else:
                child_word_dict = node.export(stem + char)
                found_words.update(child_word_dict)

        return found_words

    def solve(self, stem, center_letter, letters):
        """Returns full content of input string"""
        found_words = []
        for char, node in self.children.items():
            if char == "*":
                if center_letter in stem:
                    found_words.append(stem)
                continue
            if char not in letters:
                continue
            child_words = node.solve(stem + char, center_letter, letters)
            for child_word in child_words:
                found_words.append(child_word)

        return found_words

    def is_empty(self):
        return self.children == {}


class Trie:
    def __init__(self) -> None:
        self.root = Node("", root=True)

    def contains(self, input_str):
        """Checks if structure contains input word"""
        pass

    def add(self, input_str, score: int = 0):
        """Adds word to Trie"""
        self.root.add(input_str, score)

    def check(self, input_str):
        """Checks trie for input string"""
        return self.root.check(input_str)

    def dump(self):
        """Returns list of words in the trie"""
        return self.root.dump("")

    def accept_word(self, word):
        """Increments score of accepted word"""
        if not self.check(word):
            self.root.add(word)

        self.root.adjust_word_score(word, 1)

    def reject_word(self, word):
        """Increments score of accepted word"""
        self.root.adjust_word_score(word, -1)

    def solve(self, letters, center_letter=None):
        """Returns a list of words that use only the given letters"""
        if not center_letter:
            center_letter = letters[0]
        return self.root.solve("", center_letter, letters)

    def play(self, letters):
        """Guides person throught the game, adjusting dictionary scores"""

        solved_words = self.solve(letters)

        acceptable_responses = set(["y", "n"])
        for word in solved_words:
            response_acceptable = False
            while not response_acceptable:
                prompt_str = "Is {} a word? Y/n: ".format(word)
                is_word = input(prompt_str)
                try:
                    is_word = is_word.strip().lower()
                except TypeError:
                    print("Invalid input response")
                    continue
                if is_word in acceptable_responses:
                    response_acceptable = True
                    if is_word == "y":
                        self.accept_word(word)
                    else:
                        self.reject_word(word)
                else:
                    print("Input not understood, try again")

    def retrospective(self, letters):
        """Updates dictionary with past words"""
        input_str = input("Please enter the first word: ")
        entered_words = []
        while input_str != "q":
            if input_str == " ":
                entered_words.pop()
            else:
                entered_words.append(input_str.lower())
            input_str = input("Next word: ")

        solved_wordset = set(self.solve(letters))
        entered_set = set(entered_words)
        bad_wordset = solved_wordset.difference(entered_set)

        for good_word in list(entered_set):
            self.accept_word(good_word)

        for bad_word in list(bad_wordset):
            self.reject_word(bad_word)

    def import_from_txt_file(self, filename):
        with open(filename) as fd:
            for line in fd:
                word = line.strip()
                if len(word) > 3:
                    self.add(word)

    def import_from_json_file(self, filename):
        try:
            with open(filename) as fd:
                data = fd.read()
                trie_dict = json.loads(data)
                for word, score in trie_dict.items():
                    self.add(word, score=score)
        except FileNotFoundError:
            pass

    def export_to_json_file(self, filename):
        export_data = self.root.export("")
        with open(filename, "w") as fd:
            json.dump(export_data, fd)

    def is_empty(self):
        return self.root.is_empty()

