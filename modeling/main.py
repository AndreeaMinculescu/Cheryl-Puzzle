from puzzle_formalism import Puzzle
from epistemic_model import EpistemicModel
from random_model import RandomModel
from utilities import draw_model
from collections import Counter

MAX_TOM_LEVEL = 4
MAX_ITERATIONS = 5
MODEL_TYPE = RandomModel


if __name__ == "__main__":
    # iterate through all levels of ToM
    for level in range(MAX_TOM_LEVEL):
        list_answers = []
        # iterate through "participants"
        for _ in range(MAX_ITERATIONS):
            # define puzzle
            cb = Puzzle(list_players=["Al", "Be"], visibility=[[True, False], [False, True]])
            # define level of ToM
            cb.set_level(level=level)
            # define model
            model = MODEL_TYPE(puzzle=cb)
            # solve puzzle and return answer
            list_answers.append(model.run_model_once())
        print(f"Current level: {level+1}")
        print(f"\t {Counter(list_answers)}")




