import pandas as pd
import re
import random
from puzzle import format_instruction_text
import glob
import numpy as np
import matplotlib.pyplot as plt


def compute_mean_dict(d):
    """
    Given a dictionary of lists, compute the mean for each list
    :param d: the dictionary
    :return: a new dictionary with the same keys as d, but with means as values
    """
    mean_d = {}
    for key in d.keys():
        mean_d[key] = np.nanmean(d[key])
    return mean_d


def combine_csvs_by_title(title):
    """
    Given a number of csvs containing a specified string in their titles, aggregate all csvs into one document
    :param title: string to be found in the titles
    :return: the merged csv
    """
    all_dfs = []

    # find all files with a specified string in the title
    for file_name in glob.glob(f"{title}*.csv"):
        df_temp = pd.read_csv(file_name)
        all_dfs.append(df_temp)

    # merge all files into one csv
    merged_df = pd.concat(all_dfs)
    return merged_df


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
    Compute monetary reward: randomly select puzzle and add 0.25 euros to the base reward of 7.5 euros if the
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
    Randomly select series of 8 puzzles, following a specified two-block design
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


# dictionaries that encode the one-to-one relation between the birthday vs all other scenarios
# used to generate new entries for the question bank, not relevant for the work flow

birthday_original = {"May": "May", "June": "June", "July": "July", "August": "August", "September": "September",
                     "14": 14, "15": 15, "16": 16, "17": 17, "18": 18}
birthday_new_month = {"May": "September", "June": "August", "July": "July", "August": "June", "September": "May",
                      "14": 14, "15": 15, "16": 16, "17": 17, "18": 18}
birthday_new_day = {"May": "May", "June": "June", "July": "July", "August": "August", "September": "September",
                    "14": 18, "15": 17, "16": 16, "17": 15, "18": 14}
birthday_new_month_day = {"May": "September", "June": "August", "July": "July", "August": "June", "September": "May",
                          "14": 18, "15": 17, "16": 16, "17": 15, "18": 14}

drink = {"May": "Extra small", "June": "Small", "July": "Regular", "August": "Large", "September": "Extra large",
         "14": "hot", "15": "lukewarm", "16": "room temperature", "17": "cold", "18": "iced"}
toy = {"May": "On the table", "June": "On the bed", "July": "On the floor", "August": "On the armchair",
       "September": "On the windowsill", "14": "doll", "15": "bunny", "16": "clown", "17": "cat", "18": "train"}
hair = {"May": "Curly", "June": "Spiky", "July": "Straight", "August": "Pixie", "September": "With bangs",
        "14": "green", "15": "blue", "16": "purple", "17": "pink", "18": "orange"}

birthday_to_bday = {str(v): str(k) for (k, v) in birthday_original.items()}
drink_to_bday = {v: k for (k, v) in drink.items()}
toy_to_bday = {v: k for (k, v) in toy.items()}
hair_to_bday = {v: k for (k, v) in hair.items()}


def translate_answer(ans, scenario, config_key):
    """
    Given an answer to a puzzle and a scenario type, return the answer translated to the original birthday scenario
    :param ans: original answer
    :param scenario: scenario type
    :param config_key: configuration key (mirroring), can be found in question_bank.csv under Translation key
    :return: the translated answer
    """
    scenario_key = eval(f"{scenario}_to_bday")
    new_answer = [scenario_key[x] for x in ans]
    new_answer = [config_key[x] for x in new_answer]
    return str(new_answer[0]) + ", " + str(new_answer[1])


def get_level_and_scen():
    """
    Helping function: for each puzzle index in the "All answer_all" dataframe, find the level and scenario from
    "question_bank" and update "All answers_all"
    """
    all_questions = pd.read_csv("question_bank.csv")
    all_answers = pd.read_csv("All answers_all.csv")
    all_answers.reset_index(inplace=True, drop=True)
    all_answers["Level"] = None
    all_answers["Scenario"] = None

    # for each puzzle in "All answers_all"
    for (idx, row) in all_answers.iterrows():
        # find the level and scenario in "question_bank" based on a common index
        if str(row["Index"]) != "nan":
            all_answers["Level"].iloc[idx] = \
                all_questions["Level of ToM"].loc[all_questions["IDX"] == row["Index"]].values[0]
            all_answers["Scenario"].iloc[idx] = \
                all_questions["Scenario"].loc[all_questions["IDX"] == row["Index"]].values[0]

    # update "All answers_all"
    all_answers.to_csv("All answers_all.csv", index=False)


#########################PLOTTING HELP FUNCTIONS#################################################

def plot_bar(data, title_plot, x_label, y_label, title_save_file):
    """
    Generate simple bar plot
    :param data: data in dictionary format
    :param title_plot: the title of the plot
    :param x_label: the label for the x-axis
    :param y_label: the label for the y-axis
    :param title_save_file: the name of the save file
    """
    plt.cla()
    plt.bar(list(data.keys()), list(data.values()), width=1.5)
    plt.xlabel(x_label)
    plt.xticks(list(data.keys()), rotation=50, fontsize=8)
    plt.ylabel(y_label)
    plt.yticks(list(data.values()))
    plt.title(title_plot)
    plt.savefig(f"{title_save_file}.png", bbox_inches='tight')


def plot_multiple_bars_per_level(data_dict, x_label, title_plot, title_save_file):
    """
    Generate plot with multiple bars per level
    :param data_dict: data in dictionary format
    :param x_label: the label for the x-axis
    :param title_plot: the title of the plot
    :param title_save_file: the name of the save file
    """
    plt.cla()
    n = len(data_dict.keys())
    r = np.arange(n)
    width = 0.2
    all_keys = list(data_dict.keys())
    all_value_levels = list(data_dict[all_keys[0]].keys())
    all_bars = []

    for (idx, v_level) in enumerate(all_value_levels):
        bar_temp = plt.bar(r + width * idx, [data_dict[key][v_level] for key in all_keys], width)
        all_bars.append(bar_temp)

    plt.xlabel(x_label)
    plt.ylabel("Frequency")
    plt.title(title_plot)

    plt.xticks(r + width, all_keys, rotation=90)
    plt.legend(all_bars, [f"Correct level-{idx + 1} ToM: " + x for (idx, x) in enumerate(all_value_levels)])
    plt.savefig(f"{title_save_file}.png", bbox_inches='tight')


def plot_violin(list_data, x_axis_levels, x_label, title_plot, title_save_file):
    """
    Generate violin plot
    :param list_data: data in list format
    :param x_axis_levels: levels on the x axis
    :param x_label: the label for the x-axis
    :param title_plot: the title of the plot
    :param title_save_file: the name of the save file
    """
    plt.cla()
    figure, ax = plt.subplots(nrows=1,
                              ncols=1,
                              figsize=(5, 7))

    ax.violinplot(list_data, list(range(len(x_axis_levels))), showmeans=True, showextrema=True)
    ax.tick_params(axis='x', rotation=90)
    ax.set_xticks(list(range(len(x_axis_levels))))
    ax.set_xticklabels(x_axis_levels)
    ax.set_title(title_plot)
    ax.set_xlabel(x_label)
    ax.set_ylabel("Time (log-transformed)")
    figure.savefig(f"{title_save_file}.png", bbox_inches='tight')


if __name__ == '__main__':
    pass
