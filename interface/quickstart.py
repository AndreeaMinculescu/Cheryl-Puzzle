from window import Window
from utilities import compute_reward
from puzzle import PuzzleApp
from background_form import FormApp
from practice_trials import PracticeApp
import time
import random
import pandas as pd
import uuid

# display and run practice trials
root = Window("Practice Trials")
app = PracticeApp(root)
root.mainloop()

# store answers to puzzle
all_answers = []
# set max number of puzzles (after which, experiment ends)
no_puzzles = 8

# read in the questions from the question bank
questions = pd.read_csv("question_bank.csv")

# store start time of experiment
start_time = time.time()

# generate unique id for participant and get puzzle list
unique_id = uuid.uuid4()
puzzle_entries = pd.read_csv("Participant puzzles.csv")
idx_list = list(puzzle_entries.iloc[app.participant_no])
idx_list.insert(int(no_puzzles/2), None)
print(idx_list)

# for each puzzle...
for (count, idx) in enumerate(idx_list):
    all_answers.append({"Subject id": unique_id, "Puzzle series no": app.participant_no, "Index": None,
                        "Correct answer": None, "Given answer": None, "Time": None})

    if idx:
        all_answers[-1]["Index"] = questions['IDX'][idx]
        all_answers[-1]["Correct answer"] = questions['Correct answer'][idx]

    # format puzzle window
    root.change_title("Cheryl's Puzzle")
    puzzle = PuzzleApp(root, idx, count, no_puzzles, all_answers, start_time)
    root.mainloop()

    try:
        # update start time of current puzzle
        start_time += all_answers[-1]["Time"]
    except TypeError:
        # if TypeError, then the experiment ended before the participant had a chance to answer, which means that time
        # ran out, so don't show the rest of the puzzles (if any left)
        break

# quit the puzzle window
root.destroy()
# compute monetary reward
reward_idx, reward_sum = compute_reward([answer for answer in all_answers if answer["Index"] is not None])
print(f"Congratulations! You earned {reward_sum} euros for {reward_idx}!")
# store answers in dataframe and export to csv
df_answers = pd.DataFrame(all_answers)
df_answers.to_csv(f"Puzzle Answers_{unique_id}.csv", index=False)

print(all_answers)

# display and run background form
root = Window("Participant Information Form")
# root.change_title("Participant Information Form")
app = FormApp(root, all_answers, unique_id, reward_sum, reward_idx)
root.mainloop()


