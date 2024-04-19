from utilities import format_text_states, draw_model
from formula import NOT, KNOW, PropositionalAtom, Operator

UPDATE_COUNT = 0


class EpistemicModel:
    def __init__(self, puzzle):
        """
        Class that generates the Kripke model associated with a puzzle and processes public announcements
        """
        # the puzzle specifications
        self.puzzle = puzzle
        # the current Kripke model graph
        self.curr_graph = self.puzzle.generate_full_model()
        # dictionary that keeps track of whether each state should be removed from the Kripke model
        self.curr_states = {node: False for node in list(self.curr_graph)}

    def process_announcement(self, formula: Operator | PropositionalAtom, curr_worlds, flag_negate=False):
        """
        Given a public announcement as a formula, finds the states in the Kripke model where the formula is not valid.
        This is implemented as a recursive function.

        Importantly, in the comments below, "level" refers to a hierarchy level in the recursive definition of a
        formula, rather than to a level of ToM

        :param formula: the public announcement (must be of type propositional atom or operator)
        :param curr_worlds: the worlds where the validity of the public announcement is tested
        :param flag_negate: a boolean to indicate if the public announcement formula is of type NOT at the
        top-most level
        """
        # counter for the number of time update_model was called
        global UPDATE_COUNT
        UPDATE_COUNT += 1

        # if the public announcement formula is of type Propositional Atom at the top-most level, then simply check
        # if the agent knows the birthday
        if isinstance(formula, PropositionalAtom):
            return self.check_validity(curr_worlds, flag_negate=flag_negate)

        # if the public announcement formula is of type NOT at the top-most level, then flip the sign of flag_negate and
        # call the function on the formula at one level lower
        if isinstance(formula, NOT):
            return self.process_announcement(formula.formula, curr_worlds=curr_worlds, flag_negate=not flag_negate)

        # if the public announcement formula is of type KNOW at the top-most level...
        if isinstance(formula, KNOW):
            # ... then for each world,...
            for world in curr_worlds.keys():
                # ... identify the agent and its Kripke relations,...
                agent_idx = list(self.puzzle.players.values()).index(formula.agent)
                uncertainty_player = self.puzzle.all_uncertainty[self.puzzle.curr_level][agent_idx]

                # ... identify the accessible worlds...
                curr_accessible_worlds = self.get_accessible_worlds(uncertainty_player, world)
                # ... and call the function on the formula at one level lower and consider the accessible worlds as the
                # new "current" worlds
                curr_worlds[world] = self.process_announcement(formula.formula,
                                                               {node: False for node in curr_accessible_worlds},
                                                               flag_negate=flag_negate)
            # if any of the worlds at one level lower was marked to be removed, then the world at the current level
            # should also be removed
            return any(curr_worlds.values())

    @staticmethod
    def get_accessible_worlds(relations, world):
        """
        Given a world w and a list of relations, finds all accessible worlds from w.

        :param relations: the list of relations belonging to an agent/player
        :param world: the world w
        :return: the list of accessible worlds from w
        """
        accessible_worlds_idx = {y for (x, y) in relations if x == world}
        return accessible_worlds_idx

    @staticmethod
    def check_validity(list_accessible_worlds, flag_negate=False):
        """
        Given a list of worlds, determines whether the player can know the birthday. This is done according to the
        following rule:
            if the list of worlds contains more than exactly one world, then the agent cannot differentiate between
            those worlds and, therefore, cannot know the birthday
            if the list of worlds contains exactly one world, then the agent considers exactly one world to be the
            birthday and, therefore, the agent knows the birthday

        :param list_accessible_worlds: the list of worlds the agent considers as candidates for the birthday
        :param flag_negate: manages formulas of type NOT (essentially, opposite behaviour from how a formula without
        NOT is handled)
        :return: True if the agent knows the birthday, False otherwise
        """
        if bool(len(list_accessible_worlds) != 1) is not flag_negate:
            return True
        return False

    def update_model(self):
        """
        Removes all states that should be removed and updates the uncertainty of the players
        """
        # remove nodes where the public announcement formula does not hold
        self.curr_graph.remove_nodes_from([node for node in self.curr_states.keys() if self.curr_states[node]])
        # update the list of current states
        self.curr_states = {node: None for node in list(self.curr_graph)}
        # update the uncertainty of all players: relations associated with removed worlds are also removed
        for idx_player in range(len(self.puzzle.players)):
            self.puzzle.update_uncertainty(idx_player, self.curr_states.keys())

    def run_model_once(self):
        """
        Processes all public announcement and updates the Kripke model

        :return: the left-over state(s) after all public announcement have been applied
        """
        # iterate through all public announcements associated with the current level...
        for idx, ann in enumerate(self.puzzle.all_announcements[self.puzzle.curr_level]):
            # ... update model based on announcement...
            self.process_announcement(ann, self.curr_states)
            # ... and update the Kripke graph
            self.update_model()

        return self.get_answer()

    def get_answer(self):
        """
        Retrieve the states of the graph and format to puzzle answer

        :return: the state label, "No solution" or "Multiple solutions"
        """
        answer_list = list(self.curr_graph)

        if len(answer_list) == 0:
            return "No solution"
        elif len(answer_list) == 1:
            return format_text_states(self.puzzle.all_states[self.puzzle.curr_level][answer_list[0]])
        else:
            return "Multiple solutions"


if __name__ == "__main__":
    pass
