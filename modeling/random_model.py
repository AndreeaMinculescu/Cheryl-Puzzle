import numpy as np
from utilities import format_text_states
import random

SEED = 42


class RandomModel:
    def __init__(self, puzzle):
        """
        Class that randomly selects a possible answer
        """
        # the puzzle specifications
        self.puzzle = puzzle
        # the current Kripke model graph
        self.curr_graph = self.puzzle.generate_full_model()

    def run_model_once(self):
        list_possible_answers = list(self.curr_graph) + ["Multiple solutions", "No solution"]
        random.seed(SEED)
        seed_no = random.randint(0, 10000)
        random.seed(seed_no)
        selected_answer = random.choice(list_possible_answers)
        if isinstance(selected_answer, str):
            return selected_answer
        return format_text_states(self.puzzle.all_states[self.puzzle.curr_level][selected_answer])
