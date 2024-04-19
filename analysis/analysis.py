import glob
import pandas as pd
import numpy as np
import matplotlib
import re
from statistics import mean, median

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
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


def get_accuracy_per_level_and_scenario():
    """
    For each ToM level and scenario, compute the mean accuracy as
                # of correct answers/ # of answers
    """
    df = pd.read_csv("All answers_puzzles all trials.csv")
    dict_tom = {1: [], 2: [], 3: [], 4: []}
    dict_scenario = {"birthday": [], "hair": [], "drink": [], "toy": []}

    # for each ToM level and each scenario, check whether answer is correct
    for (idx, row) in df.iterrows():
        dict_tom[row["Level"]].append(row["Is.correct"])
        dict_scenario[row["Scenario"]].append(row["Is.correct"])

    print(dict_tom)
    print(compute_mean_dict(dict_tom))
    print(dict_scenario)
    print(compute_mean_dict(dict_scenario))


def plot_accuracy_per_participant():
    """
    For each participant, compute the mean accuracy over all completed puzzles. Then, plot the frequency of the
    accuracy values in a bar plot.
    """
    all_accuracies = []
    all_answers = pd.read_csv("All answers_puzzles all trials.csv")
    # compute and store all the mean accuracy over all completed puzzles for each participant
    for subject_id in set(all_answers["Subject.id"]):
        df_temp = all_answers.loc[all_answers["Subject.id"] == subject_id]
        no_correct_answers = len(df_temp[df_temp['Is.correct'] == 1])
        all_accuracies.append(no_correct_answers / len(df_temp) * 100)

    plot_bar(dict(sorted(dict(Counter(all_accuracies)).items())), "Distribution of accuracy over participants",
             "Accuracy (%) over the 8 puzzles", "Number of participants", "plots/distrib_acc_participants",
             rotation_x=0)


def count_no_entries_per_participant():
    """
    Count how many puzzles each participant solved. Then, show how many participants finished how many puzzle
    """
    all_count = []
    all_answers = pd.read_csv("All answers_puzzles.csv")
    for subject_id in set(all_answers["Subject.id"]):
        df_temp = all_answers.loc[all_answers["Subject.id"] == subject_id]
        all_count.append(len(df_temp))

    print(Counter(all_count))


def plot_time_distribution():
    """
    Plot the log-time distribution of solving a puzzle for:
        1) each ToM level
        2) each scenario
        3) each ToM level x scenario combination
    in three separate violin plots
    """
    df = pd.read_csv("All answers_puzzles all trials.csv")
    dict_tom = {1: [], 2: [], 3: [], 4: []}
    dict_scenario = {"birthday": [], "hair": [], "drink": [], "toy": []}
    dict_interaction = {}

    # for each ToM level, scenario and combination, store the log-transformed times
    for (idx, row) in df.iterrows():
        dict_tom[row["Level"]].append(row["logTime"])
        # for scenarios, only consider the second block
        if row["Block"] == 2:
            dict_scenario[row["Scenario"]].append(row["logTime"])
            try:
                dict_interaction[f"{row['Scenario']}-{row['Level']}"].append(row['logTime'])
            except KeyError:
                dict_interaction[f"{row['Scenario']}-{row['Level']}"] = [row['logTime']]

    print(dict_tom)
    print(compute_mean_dict(dict_tom))
    print(dict_scenario)
    print(compute_mean_dict(dict_scenario))
    print(dict_interaction)
    print(compute_mean_dict(dict_interaction))

    plot_violin(list(dict_tom.values()), list(dict_tom.keys()), "Level of ToM",
                "Distribution of log-transformed time over ToM levels", "plots/tom_log_time_distrib")
    plot_violin(list(dict_scenario.values()), list(dict_scenario.keys()), "Scenario",
                "Distribution of log-transformed time over scenarios", "plots/scenario_log_time_distrib",
                rotation_x=90)
    plot_violin(list(dict_interaction.values()), list(dict_interaction.keys()), "Scenario-ToM level",
                "Distribution of log-transformed time over scenarios and ToM levels",
                "plots/scenario_level_log_time_distrib", rotation_x=90)


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
    print("mean: ", mean([eval(elem) for elem in list(df_pb["Given answer"])]))
    print("median: ", median([eval(elem) for elem in list(df_pb["Given answer"])]))
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
             "plots/p-beauty_distrib")


def plot_distrib_answers():
    """
    For each of the four original birthday puzzles, plot the frequency of all answers in a bar plot
    """
    df = pd.read_csv("All answers_all.csv")
    df["Translated answer"] = None
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
                transl_answer = translate_answer(row["Given answer"].split(", "), scenario, eval(transl_key))
            except KeyError:
                transl_answer = row["Given answer"]
            # then, store it as a given answer for the corresponding original puzzle
            if transl_answer not in dict_tom.keys():
                dict_tom[transl_answer] = {'May, 15': 0, 'September, 14': 0, 'September, 15': 0, 'May, 18': 0}
                dict_tom[transl_answer][correct_answer] = 1
            else:
                dict_tom[transl_answer][correct_answer] += 1

    sorted_dict_tom = dict(sorted(list(dict_tom.items())[3:]))
    sorted_dict_tom.update(dict(list(dict_tom.items())[:3]))
    plot_multiple_bars_per_level(sorted_dict_tom, "Option chosen", "Distribution of answers per puzzle type",
                                 "plots/distrib_answers_puzzle")


if __name__ == '__main__':
    get_form_data()
    get_accuracy_per_level_and_scenario()
    plot_accuracy_per_participant()
    count_no_entries_per_participant()
    plot_time_distribution()
    plot_p_beauty()
    plot_distrib_answers()
