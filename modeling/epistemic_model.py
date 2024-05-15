import random

from utilities import format_text_states, draw_model
from formula import NOT, KNOW, PropositionalAtom, Operator, PublicAnnouncement
from solver import Solver

UPDATE_COUNT = 0


class EpistemicModel(Solver):
    def __init__(self, max_iter, max_tom_level, curr_tom_level, puzzle):
        """
        Solver that generates the Kripke model associated with a puzzle and processes public announcements
        """
        super().__init__(max_iter, max_tom_level, curr_tom_level, puzzle)
        # dictionary that keeps track of whether each state should be removed from the Kripke model
        self.curr_states = None

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
                uncertainty_player = self.all_uncertainty[self.curr_level][agent_idx]

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

    def update_model(self, graph):
        """
        Removes all states that should be removed and updates the uncertainty of the players
        """
        # remove nodes where the public announcement formula does not hold
        graph.remove_nodes_from([node for node in self.curr_states.keys() if self.curr_states[node]])
        # update the list of current states
        self.curr_states = {node: None for node in list(graph)}
        # update the uncertainty of all players: relations associated with removed worlds are also removed
        for idx_player in range(len(self.puzzle.players)):
            self.update_uncertainty(idx_player, self.curr_states.keys())
        return graph

    def cut_operators(self, formula, wanted_level, cutting_direction):
        """
        Main logic for the cut operator model: recursively remove one random knowledge operator from a formula until
        the formula has (at most) the desired ToM level

        :param formula: the formula to be adjusted
        :param wanted_level: the expected ToM level
        :param cutting_direction: the direction in which knowledge statements are removed by the cutting model until
        the statement is of at most "wanted_level" ToM level; lr means that the left-most knowledge operator in the
        formula is removed first; rl means that the right-most knowledge operator in the formula is removed first
        :return: the formula with the expected ToM level
        """
        # if the formula has the expected ToM level, then return it as a public announcement
        if formula.tom_level <= wanted_level:
            return PublicAnnouncement(formula)

        # otherwise, randomly choose a depth and remove the knowledge operator (and associated NOT operator
        # if applicable) at that depth
        if cutting_direction == "lr":
            new_formula = self.remove_operator_at_depth(formula, 0)
        elif cutting_direction == "rl":
            new_formula = self.remove_operator_at_depth(formula, formula.tom_level-1)
        else:
            raise NotImplementedError("Unknown cutting direction! Please first specify cutting behaviour!")
        return self.cut_operators(new_formula, wanted_level, cutting_direction)

    def remove_operator_at_depth(self, formula, curr_depth):
        """
        Recursively removes a knowledge operator at a specified depth

        :param formula: the original formula
        :param curr_depth: the depth of interest
        :return: the formula with the removed knowledge operator
        """
        # if the formula at the top-most depth is of type KNOW...
        if isinstance(formula, KNOW):
            # if the knowledge operator is at the desired depth, then remove it and return the remainder
            if curr_depth == 0:
                return formula.formula

            # otherwise, reduce the depth by 1
            # NOTE: for NOT to be removed alongside the knowledge operator, counter must always reach 0 right after
            # the last knowledge operator to be ignored
            curr_depth -= 1
            # keep the knowledge operator and process the next depth
            return KNOW(self.remove_operator_at_depth(formula.formula, curr_depth), formula.agent)

        # if the formula at the top-most depth is of type NOT...
        elif isinstance(formula, NOT):
            # if the NOT operator is at the desired depth and is followed by a knowledge operator, then remove the NOT
            # operator alongside the knowledge operator
            # NOTE: if the NOT operator should stay, then simply remove everything except the statement under else
            if curr_depth == 0 and isinstance(formula.formula, KNOW):
                return self.remove_operator_at_depth(formula.formula, curr_depth)
            # otherwise, keep the NOT operator and process the next depth
            else:
                return NOT(self.remove_operator_at_depth(formula.formula, curr_depth))

        # if the formula at the top-most depth not of type KNOW or NOT, then make sure to implement the logic!!
        else:
            raise NotImplementedError("Operator logic in remove_operator_at_death not implemented")

    def run_model_once(self, init_graph, model_level=None, cutting_direction="lr", draw=False, save_file_name="temp"):
        """
        Processes all public announcement and updates the Kripke model

        :param init_graph: the initial Kripke graph on which the public announcements are applied
        :param model_level: the maximum ToM level that the model can process (if None, then the model can process
        any ToM statement)
        :param cutting_direction: the direction in which knowledge statements are removed by the cutting model until
        the statement is of at most "model_level" ToM level
        :param draw: if True then the intermediary Kripke models after each public announcement is drawn and saved to
        a png
        :param save_file_name: the path to save the pngs at (applicable if draw is set to True)
        :return: the left-over state(s) after all public announcement have been applied
        """
        assert len(self.puzzle.all_announcements[self.curr_level]), \
            "Please specify at least one public announcement!"

        self.curr_states = {node: False for node in list(init_graph)}

        # iterate through all public announcements associated with the current level
        for idx, ann in enumerate(self.puzzle.all_announcements[self.curr_level]):
            # check that announcement is of the correct type
            if not isinstance(ann, PublicAnnouncement):
                raise TypeError("Public announcement must be of type PublicAnnouncement!")
            # potentially cut off operators
            if model_level:
                ann = self.cut_operators(ann.formula, model_level, cutting_direction)
            # update model based on announcement
            self.process_announcement(ann.formula, self.curr_states)
            # update the Kripke graph
            updated_graph = self.update_model(init_graph)
            # potentially visualize the updated graph
            if draw:
                draw_model(updated_graph, f"{save_file_name}_{UPDATE_COUNT}")

        return self.get_answer(updated_graph)

    def get_answer(self, graph):
        """
        Retrieve the states of the graph and format to puzzle answer

        :return: the state label, "No solution" or "Multiple solutions"
        """
        answer_list = list(graph)

        if len(answer_list) == 0:
            return "No solution"
        elif len(answer_list) == 1:
            return format_text_states(self.puzzle.all_states[self.curr_level][answer_list[0]])
        else:
            return "Multiple solutions"


if __name__ == "__main__":
    pass
