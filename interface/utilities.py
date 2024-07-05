import pandas as pd
import re
import random
from puzzle import format_instruction_text


def test_age_validity(age):
    """
    Test whether an age string has the correct format
    :param age: the string as input
    :return: True if the age is a number between 15 and 80, False otherwise
    """
    try:
        age = int(age)
        if age < 15 or age > 80:
            return 0
    except ValueError:
        return 0
    return 1


def test_email_validity(email):
    """
    Test whether an email string has the correct format
    :param email: the string as input
    :return: True if the string has the correct format, False otherwise
    """
    # an email should be of the form X@Y.Z, where X, Y, Z can be any combination of letters and numbers or
    # specific symbols
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None


def test_participant_no_validity(no):
    """
    Test whether the participant ID has the correct format
    :param no: the string as input
    :return: True if no is a number between 0 and the number of columns of "Participant puzzles", False otherwise
    """
    puzzle_entries = pd.read_csv("Participant puzzles.csv")
    try:
        no = int(no)
        if no < 0 or no >= len(puzzle_entries):
            return 0
    except ValueError:
        return 0
    return 1


def write_to_txt(participant_no):
    """
    Export instruction text for each participant's puzzle to a txt file
    This function is not part of the basic workflow
    """
    all_questions = pd.read_csv("question_bank.csv")
    participant_questions = pd.read_csv("Participant puzzles.csv").iloc[participant_no]
    file = open(f"../docs/Pilot/participant{participant_no}.txt", "w")

    for question_id in participant_questions:
        question = all_questions.iloc[question_id]
        print(question)
        text = format_instruction_text(eval(question["Options"]),
                                       question["Dialogue"],
                                       scenario=question["Scenario"])
        file.write(text)
        file.write("\n\n\n")

    file.close()


def write_all_to_txt():
    """
    Export instruction text for all birthday puzzles to a txt file
    This function is not part of the basic workflow
    """
    all_questions = pd.read_csv("question_bank.csv")
    # get all puzzles with the birthday scenario
    birthday_questions = all_questions.loc[all_questions['Scenario'] == "birthday"]
    # sort them by the level of ToM
    birthday_questions.sort_values(by=['Level of ToM'], inplace=True)
    file = open("question_bank.txt", "w")

    for idx, row in birthday_questions.iterrows():
        text = format_instruction_text(eval(row["Options"]),
                                       row["Dialogue"],
                                       scenario=row["Scenario"])
        file.write(text)
        file.write("\n\n\n")

    file.close()


def compute_reward(answers_list):
    """
    Compute monetary reward: randomly select puzzle and add 2.5 euros to the base reward of 7.5 euros if the
    participant answered correctly
    :param answers_list: list of answers given by participants
    :return: the index of the random puzzle, the monetary reward in euros
    """
    reward = 7.5
    bonus_reward = 2.5
    random_answer = random.choice(answers_list)
    if random_answer["Given answer"] == random_answer["Correct answer"]:
        reward += bonus_reward

    return random_answer["Index"], reward


def shuffle_two_lists(list1, list2):
    """
    Shuffle two lists together, such that no element of the original list(s) remains in the same position
    -----------------------
    Example:
        list1 = ["a", "b", "c"]
        list2 = [1, 2, 3]

        correct:
            shuffled_list1 = ["c", "a", "b"]
            shuffled_list2 = [3, 1, 2]
        wrong:
            shuffled_list1 = ["c", "a", "b"]
            shuffled_list2 = [2, 3, 1]

            shuffled_list1 = ["c", "b", "a"]
            shuffled_list2 = [3, 2, 1]
    -----------------------
    :param list1: first list
    :param list2: second list
    :return: shuffled lists
    """
    list3 = list(zip(list1, list2))
    shuffled_list = list3[:]

    while any(shuffled_list[i] == list3[i] for i in range(len(list3))):
        random.shuffle(shuffled_list)
    return zip(*shuffled_list)


def get_shuffled_list(list_scenario, list_tom):
    """
    Shuffles and associates scenarios with levels of ToM
    :param list_scenario: list of all scenarios
    :param list_tom: list of all ToM levels
    :return: shuffled list
    """
    # shuffle elements in the first half of the list
    first_half_scenario, first_half_tom = shuffle_two_lists(list_scenario[:], list_tom[:])

    # shuffle elements in the second half of the list
    second_half_scenario = first_half_scenario[:]
    second_half_tom = list_tom[:]
    second_half_scenario, second_half_tom = shuffle_two_lists(second_half_scenario[:], second_half_tom[:])

    # return both halves of the list
    return first_half_scenario + second_half_scenario, first_half_tom + second_half_tom


def generate_puzzle_list():
    """
    Randomly select series of 8 puzzles, following a specified two-block design. Create "Participant puzzles.csv"
    """
    # read in the questions from the question bank
    questions = pd.read_csv("question_bank.csv")
    # define number of participants
    no_entries = 100

    # store all entries
    store_participant_entries = []

    for _ in range(no_entries):
        # store entry per participant
        idx_list = []
        # randomly select puzzles such that there are overall 2 puzzles per level of ToM and 2 puzzles per scenario
        # additionally, make sure that no scenario gets associated the same level of ToM twice
        all_scenarios = list(set(questions['Scenario']))
        all_tom = [_ for _ in range(1, 5)]
        # TO FIX BUG, uncomment line below
        # random.shuffle(all_tom)
        scenario_list, levels_tom = get_shuffled_list(all_scenarios, all_tom)
        print(scenario_list, levels_tom)

        for idx in range(len(scenario_list)):
            temp_df = questions.loc[(questions['Scenario'] == scenario_list[idx]) &
                                    (questions['Level of ToM'] == levels_tom[idx])]
            chosen_entry = temp_df.sample()
            idx_list.append(chosen_entry.index.to_list()[0])
        store_participant_entries.append(idx_list)

    df_participant_entries = pd.DataFrame(store_participant_entries)
    df_participant_entries.to_csv("Participant puzzles.csv", index=False)


if __name__ == "__main__":
    pass
