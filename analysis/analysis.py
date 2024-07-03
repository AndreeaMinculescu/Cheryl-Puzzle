import pandas as pd
import numpy as np
import re
from statistics import mean, median
from collections import Counter
from utilities import translate_answer, compute_mean_dict, plot_bar, plot_multiple_bars_per_level, plot_violin


def get_form_data():
    """
    Aggregate all answers to the background form and write to txt
    """
    # background form answers are unique per participant
    df = pd.read_csv("All answers_all.csv")
    df.drop_duplicates(subset=['Subject id'], inplace=True)

    f = open("plots/form_data.txt", "w")
    text = ""

    text += f"All ages: {dict(Counter(df['Age']))} \n"
    text += f"\t Mean age: {np.mean(df['Age'])}, Min age: {np.min(df['Age'])}, Max age: {np.max(df['Age'])} \n\n"

    text += f"All genders: {dict(Counter(df['Gender']))} \n\n"

    text += f"Student RUG?: {dict(Counter(df['Student rug']))} \n\n"

    text += f"Student bachelor?: {dict(Counter(df['Student bachelor']))} \n\n"

    text += f"All study programs: {dict(Counter(df['Study program']))} \n\n"

    text += f"Logic course?: {dict(Counter(df['Logic course']))} \n"
    text += f"Logic course ('other' option): {df['Logic course (additional)'].values} \n\n"

    text += f"All difficulty instructions: {dict(Counter(df['Difficulty instructions']))} \n"
    text += f"\t Mean difficulty instructions: {np.mean(df['Difficulty instructions'])}, " \
            f"Min difficulty instructions: {np.min(df['Difficulty instructions'])}, " \
            f"Max difficulty instructions: {np.max(df['Difficulty instructions'])} \n"
    text += "# Note: 10 means that the instructions were easy to understand \n\n"

    text += f"All enjoy puzzle: {dict(Counter(df['Enjoy puzzle']))} \n"
    text += f"\t Mean enjoy: {np.mean(df['Enjoy puzzle'])}, " \
            f"Min enjoy: {np.min(df['Enjoy puzzle'])}, " \
            f"Max enjoy: {np.max(df['Enjoy puzzle'])} \n"
    text += "# Note: 10 means that the they enjoyed the puzzles greatly \n\n"

    text += f"All difficulty puzzle: {dict(Counter(df['Difficulty puzzle']))} \n"
    text += f"\t Mean difficulty puzzle: {np.mean(df['Difficulty puzzle'])}, " \
            f"Min difficulty puzzle: {np.min(df['Difficulty puzzle'])}, " \
            f"Max difficulty puzzle: {np.max(df['Difficulty puzzle'])} \n"
    text += "# Note: 10 means that the puzzles were very difficult \n\n"

    text += f"Know puzzle?: {dict(Counter(df['Know puzzle?']))} \n"
    text += f"Know puzzle ('other' option): {df['Know puzzle? (additional)'].values} \n\n"

    text += f"Strategy: {df['Strategy'].values} \n\n"

    text += f"All mood: {dict(Counter(df['Mood']))} \n"
    text += f"\t Mean mood: {np.mean(df['Mood'])}, " \
            f"Min mood: {np.min(df['Mood'])}, " \
            f"Max mood: {np.max(df['Mood'])} \n\n"

    text += f"Remarks: {df['Remarks'].values} \n\n"

    f.write(text)
    f.close()


def plot_accuracy_per_order_and_scenario():
    """
    For each ToM order and scenario, compute the mean accuracy as
                # of correct answers/ # of answers
    """
    df = pd.read_csv("All answers_puzzles all trials.csv")
    dict_tom = {1: [], 2: [], 3: [], 4: []}
    dict_scenario = {"birthday": [], "hair": [], "drink": [], "toy": []}

    # for each ToM order (level) and each scenario, check whether answer is correct
    for (idx, row) in df.iterrows():
        dict_tom[row["Level"]].append(row["Is.correct"])
        dict_scenario[row["Scenario"]].append(row["Is.correct"])

    dict_tom_means = compute_mean_dict(dict_tom)
    # for readability, sort scenario dict by value
    dict_scenario_means = dict(sorted(compute_mean_dict(dict_scenario).items(), key=lambda item: item[1], reverse=True))

    plot_bar(dict_tom_means, "Accuracy per ToM Order", "ToM order", "Accuracy (%) over the 8 puzzles", (0, 100),
             (1, len(dict_tom_means)), title_save_file="plots/acc_per_order", rotation_x=0, chance_y=1 / 13 * 100,
             bar_width=0.5)
    plot_bar(dict_scenario_means, "Accuracy per Scenario", "Scenario", "Accuracy (%) over the 8 puzzles", (0, 100),
             (0, len(dict_scenario_means) - 1), title_save_file="plots/acc_per_scen", rotation_x=0,
             chance_y=1 / 13 * 100,
             bar_width=0.5)


def plot_accuracy_per_participant():
    """
    For each participant, compute the mean accuracy over all completed puzzles. Then, plot the frequency of the
    accuracy values in a bar plot.
    """
    all_accuracies = {x / 8 * 100: 0 for x in range(9)}
    all_answers = pd.read_csv("All answers_puzzles all trials.csv")
    # compute and store all the mean accuracy over all completed puzzles for each participant
    for subject_id in set(all_answers["Subject.id"]):
        df_temp = all_answers.loc[all_answers["Subject.id"] == subject_id]
        no_correct_answers = len(df_temp[df_temp['Is.correct'] == 1])
        accuracy = no_correct_answers / len(df_temp) * 100
        all_accuracies[accuracy] += 1

    plot_bar(all_accuracies, "Distribution of accuracy over participants", "Accuracy (%) over the 8 puzzles",
             "Number of participants", (0, max(all_accuracies.values())), (0, max(all_accuracies.keys())),
             "plots/distrib_acc_participants", chance_x=1 / 13 * 100, rotation_x=0, bar_width=5)


def count_no_entries_per_participant():
    """
    Count how many puzzles each participant solved. Then, show how many participants finished how many puzzle
    """
    all_count = []
    all_answers = pd.read_csv("All answers_puzzles.csv")
    for subject_id in set(all_answers["Subject.id"]):
        df_temp = all_answers.loc[all_answers["Subject.id"] == subject_id]
        all_count.append(len(df_temp))

    print("Number of trials completed: Number of participants", dict(Counter(all_count)))


def plot_time_distribution(log_bool=False):
    """
    Plot the log-time distribution of solving a puzzle for:
        1) each ToM order
        2) each scenario
    in three separate violin plots

    :param log_bool: if True, then log-transformed time is plotted
    """
    df = pd.read_csv("All answers_puzzles all trials.csv")
    dict_tom = {1: [], 2: [], 3: [], 4: []}
    dict_scenario = {"birthday": [], "hair": [], "drink": [], "toy": []}

    # for each ToM order (level), scenario and combination, store the log-transformed times
    for (idx, row) in df.iterrows():
        time = row["logTime"] if log_bool else row["Time"]
        dict_tom[row["Level"]].append(time)
        # for scenarios, only consider the second block
        if row["Block"] == 2:
            dict_scenario[row["Scenario"]].append(time)

    # for readability, sort by mean of values
    dict_scenario_sorted = dict(sorted(dict_scenario.items(), key=lambda item: mean(item[1])))

    y_axis_label = "Time (log-transformed)" if log_bool else "Time (in seconds)"
    plot_violin(list(dict_tom.values()), list(dict_tom.keys()), "ToM order", y_axis_label, (0, 800),
                "Distribution of Time over ToM Orders", "plots/tom_time_distrib")
    plot_violin(list(dict_scenario_sorted.values()), list(dict_scenario_sorted.keys()), "Scenario", y_axis_label,
                (0, 800), "Distribution of Time over Scenarios", "plots/scenario_time_distrib")


def plot_p_beauty(bin_size=20):
    """
    Plot the binned distribution of the p-beauty answers.

    :param bin_size: the number of bins
    """
    df = pd.read_csv("All answers_all.csv")
    # get only the p-beauty answers
    df_pb = df[df['Index'].isnull()]
    # count how many participants gave the same answer
    dict_answers = dict(Counter(list(df_pb["Given answer"])))
    # find the thresholds for the specified number of bins
    bins = np.linspace(0, 100, bin_size, dtype=int)
    # create a dictionary where the keys are intervals between two extrema of each bin
    dict_binned_answers = {f"({bins[idx - 1]}, {bins[idx]}]": 0 for idx in range(1, len(bins))}

    # for each p-beauty answer...
    for ans in dict_answers.keys():
        # for each binned interval...
        for str_binned_interval in dict_binned_answers.keys():
            # find the extrema values for each binned interval...
            binned_interval = re.findall(r'\d+', str_binned_interval)
            # if the p-beauty answer is within that binned interval, update the dict
            if int(binned_interval[0]) < int(ans) <= int(binned_interval[1]):
                dict_binned_answers[str_binned_interval] += dict_answers[ans]
                break

    plot_bar(dict_binned_answers, "P-beauty distribution", "Value interval", "Number of participants",
             (0, max(dict_binned_answers.values())), (0, len(dict_binned_answers)), "plots/p-beauty_distrib")


def plot_distrib_answers():
    """
    For each of the four original birthday puzzles, plot the frequency of all answers in a bar plot
    """
    df = pd.read_csv("All answers_puzzles.csv")
    question_bank = pd.read_csv("../interface/question_bank.csv")
    dict_tom = {"I don't know": {'May, 15': 0, 'September, 14': 0, 'September, 15': 0, 'May, 18': 0},
                "No solution": {'May, 15': 0, 'September, 14': 0, 'September, 15': 0, 'May, 18': 0},
                "Multiple solutions": {'May, 15': 0, 'September, 14': 0, 'September, 15': 0, 'May, 18': 0}}

    # for each of the four puzzles, store the answers
    for (idx, row) in df.iterrows():
        if str(row["Index"]) != "nan" and str(row["Time"]) != "nan":
            # first, translate the answer, such that the puzzle corresponds to one of the four original puzzles
            correct_answer = question_bank.loc[question_bank["IDX"] == row["Index"]]["Translated answer"].values[0]
            transl_key = question_bank.loc[question_bank["IDX"] == row["Index"]]["Translation key"].values[0]
            scenario = question_bank.loc[question_bank["IDX"] == row["Index"]]["Scenario"].values[0]
            try:
                transl_answer = translate_answer(row["Given.answer"].split(", "), scenario, eval(transl_key))
            except KeyError:
                transl_answer = row["Given.answer"]
            # then, store it as a given answer for the corresponding original puzzle
            if transl_answer not in dict_tom.keys():
                dict_tom[transl_answer] = {'May, 15': 0, 'September, 14': 0, 'September, 15': 0, 'May, 18': 0}
                dict_tom[transl_answer][correct_answer] = 1
            else:
                dict_tom[transl_answer][correct_answer] += 1

    # sort dictionary by month and day, in this order
    key_order = ["May", "June", "July", "August", "September", "Multiple solutions", "No solution", "I don't know"]
    new_tom_dict = {}
    for lookup_key in key_order:
        new_lookup_dict = {key: value for (key, value) in dict_tom.items() if lookup_key in key}
        new_lookup_dict = dict(sorted(new_lookup_dict.items()))
        new_tom_dict.update(new_lookup_dict)

    plot_multiple_bars_per_level(new_tom_dict, "Answer selected", "Distribution of answers per puzzle type",
                                 "plots/distrib_answers_puzzle")


if __name__ == '__main__':
    get_form_data()
    plot_accuracy_per_order_and_scenario()
    plot_accuracy_per_participant()
    count_no_entries_per_participant()
    plot_time_distribution()
    plot_p_beauty()
    plot_distrib_answers()
