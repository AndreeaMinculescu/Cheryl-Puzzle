from puzzle_formalism import Puzzle
from epistemic_model import EpistemicModel
from random_model import RandomModel
from utilities import get_common_ratio
import pandas as pd
from collections import Counter

# the highest ToM level possible
MAX_TOM_LEVEL = 4
# the maximum number of iterations per ToM level
MAX_ITERATIONS = 84
# the type of the model (can be either RandomModel or EpistemicModel)
MODEL_TYPE = EpistemicModel
# dictionary of keyword argument for the run_model_once function (NOTE: function must be implemented for all model)
KWARGS = {EpistemicModel: {"model_level": 1, "cutting_direction": "lr", "draw":False, "save_file_name":"./tmp"},
          RandomModel: {}}
# path to file to save results in
FILE_PATH = "results.txt"


if __name__ == "__main__":
    # read in the participants' answers
    subj_df = pd.read_csv("../analysis/All answers_puzzles all trials.csv")

    # define puzzle
    cb = Puzzle(list_players=["Al", "Be"], visibility=[[True, False], [False, True]])

    # open file to save results in
    f = open(FILE_PATH, "a+")
    f.write(f"\nModel configuration: {str(MODEL_TYPE)} - {KWARGS[MODEL_TYPE]}\n\n")

    # iterate through all levels of ToM
    for level in range(3,MAX_TOM_LEVEL):
        # initialize solver object
        solver = MODEL_TYPE(MAX_ITERATIONS, MAX_TOM_LEVEL, level, cb)
        # initialize list to save model answers in
        list_answers = []
        # iterate through model trials (ideally should be the same as the number of participant trials)
        for _ in range(MAX_ITERATIONS):
            # initialize Kripke graph
            graph = solver.generate_full_model()
            # solve puzzle and return answer
            list_answers.append(solver.run_model_once(graph, **KWARGS[MODEL_TYPE]))

        # save answers to file
        f.write(f"Level of ToM: {level+1}\n")
        f.write(f"\t Explained data: {get_common_ratio(list_answers, subj_df.loc[subj_df['Level'] == level+1]['Translated.answer'].values)}\n")
        f.write(f"\t Model answers: {dict(Counter(list_answers))}\n")

    f.close()




