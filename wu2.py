from json import load
from string import ascii_lowercase
from copy import deepcopy
import constants as c


class Wordle_Unlimited:
    @staticmethod
    def __get_cans():
        with open("resources/cans.json", "r") as f:
            return load(f)

    @staticmethod
    def __get_cants():
        with open("resources/cants.json", "r") as f:
            return load(f)

    def __init__(self):
        self.cans = self.__get_cans()
        self.cants = self.__get_cants()

        self.repeats = {}
        self.repeats_min = {}
        self.whites = [
            set([letter for letter in ascii_lowercase]) for _ in range(c.SPOTS)
        ]
        self.__update_whites()

        self.best_guess_s = c.GUESS_0

    def __update_whites(self):
        new_whites = []
        for spot, white in enumerate(self.whites):
            new_white = set()
            for letter in white:
                for can_s in self.cans:
                    if letter == can_s[spot]:
                        new_white.add(letter)
                        break
            new_whites.append(new_white)
        self.whites = new_whites

    def __update_info(self, guess_d, colors):
        m_new_repeats = set()
        freqs = {letter: 0 for letter in guess_d}

        for letter in guess_d:
            for spot in guess_d[letter]:
                # 5 loops
                if colors[spot] == "2":
                    # this spot only has this letter
                    self.whites[spot] = [letter]
                    freqs[letter] += 1

                else:
                    # this spot cannot have this letter
                    # check other spots later
                    try:
                        self.whites[spot].remove(letter)
                    except:
                        pass
                    # => letter is another spot
                    if colors[spot] == "1":
                        freqs[letter] += 1
                    else:
                        # colors[spot] == "0"
                        m_new_repeats.add(letter)

        # maybe update repeats and repeats min
        for letter in freqs:
            freq = freqs[letter]
            if freq == 0:
                # letter is not in win
                for white in self.whites:
                    try:
                        white.remove(letter)
                    except:
                        pass
            elif letter in m_new_repeats:
                # letter is in repeat
                self.repeats[letter] = freqs[letter]
                try:
                    del self.repeats_min[letter]
                except:
                    pass
            elif letter not in self.repeats:
                # letter is in repeats min
                try:
                    if self.repeats_min[letter] < freq:
                        self.repeats_min[letter] = freq
                except:
                    self.repeats_min[letter] = freq

    def __get_is_guess_in_cants(self, guess_d):
        # if guess not in cans, remove from cans
        for letter in self.repeats:
            if letter not in guess_d:
                return True
            if self.repeats[letter] != len(guess_d[letter]):
                return True

        for letter in self.repeats_min:
            if letter not in guess_d:
                return True
            if self.repeats_min[letter] > len(guess_d[letter]):
                return True

        for letter in guess_d:
            for spot in guess_d[letter]:
                if letter not in self.whites[spot]:
                    return True

        return False

    def __update_cans(self):
        new_cans = {}
        for can_s in self.cans:
            can_d = self.cans[can_s]
            # if guess in can wins, append and remove
            if self.__get_is_guess_in_cants(guess_d=can_d):
                self.cants[can_s] = can_d
            else:
                new_cans[can_s] = can_d
        self.cans = new_cans

    def __get_remains(self, repeats, repeats_min, whites):
        # update cans
        def h_get_is_guess_in_cants(guess_d):
            # if guess not in cans, remove from cans
            for repeat in repeats:
                if repeat not in guess_d:
                    return True
                if repeats[repeat] != len(guess_d[repeat]):
                    return True

            for repeat_min in repeats_min:
                if repeat_min not in guess_d:
                    return True
                if repeats_min[repeat_min] > len(guess_d[repeat_min]):
                    return True

            for letter in guess_d:
                for spot in guess_d[letter]:
                    if letter not in whites[spot]:
                        return True

            return False

        remains = len(self.cans)
        for can_s in self.cans:
            if h_get_is_guess_in_cants(guess_d=self.cans[can_s]):
                remains -= 1
        return remains

    def __c_update_info(self, guess_d, win_d, repeats, repeats_min, whites):
        for letter in guess_d:
            if letter in win_d:
                # letter in whites
                for spot in guess_d[letter]:
                    if spot in win_d[letter]:
                        # letter is green
                        whites[spot] = [letter]
                    else:
                        # letter is yellow or gray
                        try:
                            whites[spot].remove(letter)
                        except:
                            pass

                freq = len(win_d[letter])
                if len(guess_d[letter]) > freq:
                    # letter is repeat
                    repeats[letter] = freq
                    # maybe remove from repeats min
                    try:
                        del repeats_min[letter]
                    except:
                        pass
                else:
                    # letter is repeat min
                    try:
                        if repeats_min[letter] < freq:
                            repeats_min[letter] = freq
                    except:
                        repeats_min[letter] = freq

            else:
                # letter not in whites
                for white in whites:
                    try:
                        white.remove(letter)
                    except:
                        pass

    def __get_sum_remains(self, guess_d, sum_remains_min):
        sum_remains = 0
        for win_s in self.cans:
            # dupe state
            repeats = deepcopy(self.repeats)
            repeats_min = deepcopy(self.repeats_min)
            whites = deepcopy(self.whites)

            self.__c_update_info(
                guess_d=guess_d,
                win_d=self.cans[win_s],
                repeats=repeats,
                repeats_min=repeats_min,
                whites=whites,
            )

            remains = self.__get_remains(
                repeats=repeats,
                repeats_min=repeats_min,
                whites=whites,
            )

            sum_remains += remains

            if sum_remains > sum_remains_min:
                return 0
        return sum_remains

    def __get_best_guess_s(self):
        cans_l = len(self.cans)
        if cans_l > 2:
            best_guess = ""
            sum_remains_min = cans_l**2

            for guess_s in self.cans:
                sum_remains = self.__get_sum_remains(
                    guess_d=self.cans[guess_s], sum_remains_min=sum_remains_min
                )
                if sum_remains != 0:
                    best_guess = guess_s
                    sum_remains_min = sum_remains

            for guess_s in self.cants:
                sum_remains = self.__get_sum_remains(
                    guess_d=self.cants[guess_s], sum_remains_min=sum_remains_min
                )
                if sum_remains != 0 and sum_remains < sum_remains_min:
                    best_guess = guess_s
                    sum_remains_min = sum_remains

            return best_guess

        else:
            for guess_s in self.cans:
                return guess_s

    def do_try(self, guess_s, colors):
        try:
            guess_d = self.cans[guess_s]
            del self.cans[guess_s]
        except:
            guess_d = self.cants[guess_s]
            del self.cants[guess_s]

        self.__update_info(guess_d=guess_d, colors=colors)
        # update whites first then update cans for efficiency
        self.__update_whites()
        self.__update_cans()
        self.best_guess_s = self.__get_best_guess_s()
