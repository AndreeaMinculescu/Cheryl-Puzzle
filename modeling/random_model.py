import numpy as np
from utilities import format_text_states
import random
from solver import Solver

SEED = 42


class RandomModel(Solver):
    def __init__(self, max_iter, max_tom_level, curr_tom_level, puzzle):
        """
        Solver that randomly selects a possible answer
        """
        super().__init__(max_iter, max_tom_level, curr_tom_level, puzzle)


    def run_model_once(self, graph):
        """
        Selects one random answer from the list of possible answers, based on a list of pre-specified seeds (see the
        Solver class)

        :param graph: the Kripke graph associated with the current puzzle
        :return: the randomly selected answer
        """
        # get the list of possible answers
        list_possible_answers = list(graph) + ["Multiple solutions", "No solution"]
        # get seed number (pre-determined in the Solver class)
        seed_no = self.seed_list[self.curr_level].pop()
        # set seed
        random.seed(seed_no)
        # select answer
        selected_answer = random.choice(list_possible_answers)
        # format answer
        if isinstance(selected_answer, str):
            return selected_answer
        return format_text_states(self.puzzle.all_states[self.curr_level][selected_answer])
