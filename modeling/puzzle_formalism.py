from utilities import Month, format_text_states
from formula import NOT, KNOW, PropositionalAtom, PublicAnnouncement
import networkx as nx


class Puzzle:
    def __init__(self, list_players, visibility):
        """
        Class that stores information regarding the design of the puzzle
        """
        # define states for each ToM level puzzle
        self.states_lev_one = [(Month.May, 15), (Month.May, 16), (Month.June, 17), (Month.June, 18),
                               (Month.July, 14), (Month.July, 16), (Month.August, 14), (Month.August, 17),
                               (Month.Sept, 16), (Month.Sept, 18)]
        self.states_lev_two = [(Month.May, 17), (Month.May, 18), (Month.June, 14), (Month.July, 16),
                               (Month.July, 18), (Month.August, 15), (Month.August, 16), (Month.August, 17),
                               (Month.Sept, 14), (Month.Sept, 15)]
        self.states_lev_three = [(Month.May, 15), (Month.May, 18), (Month.June, 15), (Month.June, 17),
                                 (Month.July, 14), (Month.July, 16), (Month.August, 14), (Month.August, 16),
                                 (Month.Sept, 15), (Month.Sept, 16)]
        self.states_lev_four = [(Month.May, 15), (Month.May, 18), (Month.June, 14), (Month.June, 15),
                                (Month.July, 17), (Month.July, 18), (Month.August, 16), (Month.August, 17),
                                (Month.Sept, 16), (Month.Sept, 17)]
        self.all_states = [self.states_lev_one, self.states_lev_two, self.states_lev_three, self.states_lev_four]

        # define players and their visibility (same for all puzzles)
        self.players = {f"player{i}": x for i, x in enumerate(list_players)}
        self.visibility = visibility

        # define announcements for each ToM level puzzle
        self.announcements_lev_one = [PublicAnnouncement(KNOW(PropositionalAtom("b"), str(self.players["player1"])))]
        self.announcements_lev_two = [
            PublicAnnouncement(NOT(KNOW(PropositionalAtom("b"), str(self.players["player0"])))),
            PublicAnnouncement(KNOW(PropositionalAtom("b"), str(self.players["player1"])))]
        self.announcements_lev_three = [PublicAnnouncement(
            KNOW(NOT(KNOW(PropositionalAtom("b"), str(self.players["player1"]))), str(self.players["player0"]))),
                                        PublicAnnouncement(KNOW(PropositionalAtom("b"), str(self.players["player1"])))]
        self.announcements_lev_four = [
            PublicAnnouncement(KNOW(KNOW(NOT(KNOW(PropositionalAtom("b"), str(self.players["player1"]))),
                                         str(self.players["player0"])), str(self.players["player1"]))),
            PublicAnnouncement(KNOW(PropositionalAtom("b"), str(self.players["player0"])))]

        self.all_announcements = [self.announcements_lev_one, self.announcements_lev_two,
                                  self.announcements_lev_three, self.announcements_lev_four]


if __name__ == "__main__":
    cb = Puzzle(list_players=["Al", "Be"], visibility=[[True, False], [False, True]])
    print(cb.announcements_lev_four[0])
