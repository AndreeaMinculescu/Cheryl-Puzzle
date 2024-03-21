import glob
import pandas as pd
import numpy as np
import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from collections import Counter
from utilities import translate_answer, combine_csvs_by_title, compute_mean_dict, \
    plot_bar, plot_multiple_bars_per_level, plot_violin


def get_form_data():
    """
    Aggregate all answers to the background form and write to txt
    """
    # background form answers are unique per participant
    df = combine_csvs_by_title("all_results/All answers")
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
    df = combine_csvs_by_title("all_results/All answers")
    question_bank = pd.read_csv("question_bank.csv")
    dict_tom = {1: [], 2: [], 3: [], 4: []}
    dict_scenario = {"birthday": [], "hair": [], "drink": [], "toy": []}

    # for each ToM level and each scenario, assert whether answer is correct
    for (idx, row) in df.iterrows():
        is_correct = 0
        if row["Correct answer"] == row["Given answer"]:
            is_correct = 1

        if str(row["Index"]) != "nan":
            dict_tom[question_bank.loc[question_bank["IDX"] == row["Index"]]["Level of ToM"].values[0]].append(
                is_correct)
            dict_scenario[question_bank.loc[question_bank["IDX"] == row["Index"]]["Scenario"].values[0]].append(
                is_correct)

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
    # compute and store all the mean accuracy over all completed puzzles for each participant
    for file_name in glob.glob(f"all_results/All answers*.csv"):
        df_temp = pd.read_csv(file_name)
        counter_all = 0
        counter_correct = 0
        for (idx, row) in df_temp.iterrows():
            if str(row["Index"]) != "nan" and str(row["Time"]) != "nan":
                counter_all += 1
                if row["Correct answer"] == row["Given answer"]:
                    counter_correct += 1
        all_accuracies.append(counter_correct / counter_all * 100)

    plot_bar(dict(Counter(all_accuracies)), "Distribution of accuracy over participants", "Accuracy (%) over the 8 puzzles",
             "Number of participants", "plots/distrib_acc_participants")


def count_no_entries_per_participant():
    """
    Count how many puzzles each participant solved. Then, show how many participants finished how many puzzle
    """
    all_count = []
    for file_name in glob.glob(f"all_results/All answers*.csv"):
        df_temp = pd.read_csv(file_name)
        counter_all = 0
        for (idx, row) in df_temp.iterrows():
            if str(row["Index"]) != "nan" and str(row["Time"]) != "nan":
                counter_all += 1
        all_count.append(counter_all)

    print(Counter(all_count))


def plot_time_distribution():
    """
    Plot the log-time distribution of solving a puzzle for:
        1) each ToM level
        2) each scenario
        3) each ToM level x scenario combination
    in three separate violin plots
    """
    df = combine_csvs_by_title("all_results/All answers")
    question_bank = pd.read_csv("question_bank.csv")
    dict_tom = {1: [], 2: [], 3: [], 4: []}
    dict_scenario = {"birthday": [], "hair": [], "drink": [], "toy": []}
    list_interaction = [f"{i}-{j}" for i in list(dict_scenario.keys()) for j in list(dict_tom.keys())]
    dict_interaction = {key: [] for key in list_interaction}

    # for each ToM level, scenarion and combination, store the log-transformed times
    for (idx, row) in df.iterrows():
        # ignore p-beauty entries and entries with no answer
        if str(row["Index"]) != "nan" and str(row["Time"]) != "nan":
            level_tom = question_bank.loc[question_bank["IDX"] == row["Index"]]["Level of ToM"].values[0]
            scenario = question_bank.loc[question_bank["IDX"] == row["Index"]]["Scenario"].values[0]
            dict_tom[level_tom].append(np.log(row["Time"]))
            dict_scenario[scenario].append(np.log(row["Time"]))
            dict_interaction[f"{scenario}-{level_tom}"].append(np.log(row["Time"]))

    print(dict_tom)
    print(compute_mean_dict(dict_tom))
    print(dict_scenario)
    print(compute_mean_dict(dict_scenario))
    print(dict_interaction)
    print(compute_mean_dict(dict_interaction))

    plot_violin(list(dict_tom.values()), list(dict_tom.keys()), "Level of ToM",
                "Distribution of log-transformed time over ToM levels", "plots/tom_log_time_distrib")
    plot_violin(list(dict_scenario.values()), list(dict_scenario.keys()), "Scenario",
                "Distribution of log-transformed time over scenarios", "plots/scenario_log_time_distrib")
    plot_violin(list(dict_interaction.values()), list(dict_interaction.keys()), "Scenario-ToM level",
                "Distribution of log-transformed time over scenarios and ToM levels",
                "plots/scenario_level_log_time_distrib")


def plot_p_beauty():
    """
    Plot the distribution of the p-beauty answers
    """
    df = combine_csvs_by_title("all_results/All answers")
    df_pb = df[df['Index'].isnull()]

    dict_answers = dict(Counter(list(df_pb["Given answer"])))
    # convert keys into integers
    dict_answers = {int(k):v for k,v in dict_answers.items()}
    # sort dict by key
    dict_answers = dict(sorted(dict_answers.items()))
    plot_bar(dict_answers, "P-beauty distribution", "Value", "Number of participants",
             "plots/p-beauty_distrib")


def plot_distrib_answers():
    """
    For each of the four original birthday puzzles, plot the frequency of all answers in a bar plot
    """
    df = pd.read_csv("All answers_all.csv")
    df["Translated answer"] = None
    question_bank = pd.read_csv("question_bank.csv")
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
