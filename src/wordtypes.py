class ValueFromWord:
    word_list = {}

    def __init__(self, word, plurals=False):
        word = word.lower()
        self.value = None
        if word in self.word_list.keys():
            self.value = self.word_list[word]
        else:
            if plurals:
                plural = word + "s"
                if plural in self.word_list.keys():
                    self.value = self.word_list[plural]


class NumberFromWord(ValueFromWord):

    def __init__(self, word):
        self.word_list = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
                          "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
                          "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
                          "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
                          "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40,
                          "fifty": 50, "sixty": 60,
                          "a": 1, "an": 1}
        super().__init__(word, False)


class UnitFromWord(ValueFromWord):

    def __init__(self, word):
        self.word_list = {"secs": 1, "s": 1, "seconds": 1,
                           "mins": 60, "m": 60, "minutes": 60,
                           "hrs": 3600, "h": 3600, "hours": 3600}
        super().__init__(word, True)


class FractionFromWord(ValueFromWord):

    def __init__(self, word):
        self.word_list = {"half": 0.5, "quarters": 0.25, "thirds": 0.333}
        super().__init__(word, True)
