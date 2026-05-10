from __future__ import annotations
from abc import ABC, abstractmethod


class State(ABC):
    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def check_self(self, char: str) -> bool:
        """
        function checks whether occured character is handled by current state
        """
        pass

    def check_next(self, next_char: str) -> State:
        for state in self.next_states:
            if state.check_self(next_char):
                return state
        raise NotImplementedError("rejected string")


class StartState(State):
    def __init__(self):
        super().__init__()
        self.next_states: list[State] = []

    def check_self(self, char: str) -> bool:
        return False


class TerminationState(State):
    def __init__(self) -> None:
        super().__init__()
        self.next_states: list[State] = []

    def check_self(self, char: str) -> bool:
        return False


class DotState(State):
    """state for . character (any character accepted)"""
    def __init__(self):
        super().__init__()
        self.next_states: list[State] = []

    def check_self(self, char: str) -> bool:
        return True


class AsciiState(State):
    """state for alphabet letters or numbers"""
    def __init__(self, symbol: str) -> None:
        super().__init__()
        self.next_states: list[State] = []
        self.curr_sym = symbol

    def check_self(self, curr_char: str) -> bool:
        return curr_char == self.curr_sym


class StarState(State):
    def __init__(self, checking_state: State):
        super().__init__()
        self.next_states: list[State] = []
        self.checking_state = checking_state

    def check_self(self, char: str) -> bool:
        for state in self.next_states:
            if state.check_self(char):
                return True
        return False


class PlusState(State):
    def __init__(self, checking_state: State):
        super().__init__()
        self.next_states: list[State] = []
        self.checking_state = checking_state

    def check_self(self, char: str) -> bool:
        return self.checking_state.check_self(char)


class RegexFSM:
    def __init__(self, regex_expr: str) -> None:
        self.curr_state = StartState()
        prev_state = self.curr_state
        tmp_next_state = self.curr_state

        for char in regex_expr:
            new_state = self.__init_next_state(char, prev_state, tmp_next_state)
            if isinstance(new_state, (StarState, PlusState)):
                prev_state.next_states.append(new_state)
                prev_state = new_state
            else:
                tmp_next_state.next_states.append(new_state)
                prev_state = tmp_next_state
            tmp_next_state = new_state

        tmp_next_state.next_states.append(TerminationState())

    def __init_next_state(
        self, next_token: str, prev_state: State, tmp_next_state: State
    ) -> State:
        match next_token:
            case next_token if next_token == ".":
                return DotState()
            case next_token if next_token == "*":
                star = StarState(tmp_next_state)
                prev_state.next_states.remove(tmp_next_state)
                return star
            case next_token if next_token == "+":
                plus = PlusState(tmp_next_state)
                prev_state.next_states.remove(tmp_next_state)
                return plus
            case next_token if next_token.isascii():
                return AsciiState(next_token)
            case _:
                raise AttributeError("Character is not supported")

    def _check_next_with_epsilon(self, state: State, char: str) -> State | None:
        for next_s in state.next_states:
            if isinstance(next_s, StarState):
                if next_s.checking_state.check_self(char):
                    return next_s
                result = self._check_next_with_epsilon(next_s, char)
                if result is not None:
                    return result
            elif next_s.check_self(char):
                return next_s
        return None

    def _can_terminate(self, state: State) -> bool:
        if isinstance(state, TerminationState):
            return True
        for next_s in state.next_states:
            if isinstance(next_s, TerminationState):
                return True
            if isinstance(next_s, StarState) and self._can_terminate(next_s):
                return True
        return False

    def check_string(self, s: str) -> bool:
        current_state = self.curr_state

        for char in s:
            if isinstance(current_state, (StarState, PlusState)):
                next_s = self._check_next_with_epsilon(current_state, char)
                if next_s is not None:
                    current_state = next_s
                elif current_state.checking_state.check_self(char):
                    pass
                else:
                    return False
            else:
                next_s = self._check_next_with_epsilon(current_state, char)
                if next_s is None:
                    return False
                current_state = next_s

        return self._can_terminate(current_state)


if __name__ == "__main__":
    tests = [
        ("abc", "abc", True),
        ("abc", "ab", False),
        ("abc", "abcd", False),

        ("a.c", "abc", True),
        ("a.c", "a4c", True),
        ("a.c", "ac", False),

        ("ab*c", "ac", True),
        ("ab*c", "abc", True),
        ("ab*c", "abbbc", True),
        ("ab*c", "abx", False),

        ("ab+c", "abc", True),
        ("ab+c", "abbbc", True),
        ("ab+c", "ac", False),
        ("ab+c", "ab", False),

        ("start.+end", "start1end", True),
        ("start.+end", "start---end", True),
        ("start.+end", "startend", False),

        ("a*4.+hi", "aaaaaa4uhi", True),
        ("a*4.+hi", "4uhi", True),
        ("a*4.+hi", "a4xyzhi", True),
        ("a*4.+hi", "hi", False),
        ("a*4.+hi", "4hi", False),
        ("a*4.+hi", "a4hi", False),
    ]

    all_passed = True

    for pattern, text, expected in tests:
        regex = RegexFSM(pattern)
        actual = regex.check_string(text)

        if actual != expected:
            print(f" Failed test for pattern '{pattern}':")
            print(f"   Argument of check_string: '{text}'")
            print(f"   Expected: {expected}, got: {actual}\n")
            all_passed = False

    if all_passed:
        print(" All tests passed!")
