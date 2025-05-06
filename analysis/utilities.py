import pandas as pd
import glob
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('TkAgg')
matplotlib.rc('font', size=12)


def compute_mean_dict(d):
    """
    Given a dictionary of lists, compute the mean for each list
    :param d: the dictionary
    :return: a new dictionary with the same keys as d, but with means as values
    """
    mean_d = {}
    for key in d.keys():
        mean_d[key] = round(np.nanmean(d[key]) * 100)
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
    all_questions = pd.read_csv("../interface/question_bank.csv")
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

def plot_bar(data_x, data_y, title_plot, x_label, y_label, y_range, x_range, title_save_file, orientation='vertical',
             chance_x=None, chance_y=None, rotation_x=90, rotation_y=0, bar_size=0.5):
    """
    Generate simple bar plot
    :param data_x: data on the x-axis
    :param data_y: data on the y-axis
    :param title_plot: the title of the plot
    :param x_label: the label for the x-axis
    :param y_label: the label for the y-axis
    :param y_range: range of values on the y-axis
    :param x_range: range of values on the x-axis
    :param title_save_file: the name of the save file
    :param orientation: if "vertical" then creates vertical bars, if "horizontal" then creates horizontal bars
    :param chance_x: guessing chance values on the x-axis
    :param chance_y: guessing chance values on the y-axis
    :param rotation_x: degree of rotation of the labels on the x-axis
    :param rotation_y: degree of rotation of the labels on the y-axis
    :param bar_size: width of the bars for vertical bar plots or height of the bars for horizontal bar plots
    """
    plt.cla()
    figure, ax = plt.subplots(nrows=1,
                              ncols=1,
                              figsize=(6, 2.5))
    if orientation == "vertical":
        ax.bar(data_x, data_y, edgecolor='black', width=bar_size)
    elif orientation == "horizontal":
        ax.barh(data_y, data_x, edgecolor='black', height=bar_size)
    ax.set_xlabel(x_label)
    ax.tick_params(axis='x', rotation=rotation_x)
    ax.tick_params(axis='y', rotation=rotation_y)
    ax.set_xticks(data_x)
    ax.set_ylabel(y_label)
    ax.set_yticks(data_y)
    ax.set_ylim([y_range[0]-0.25, y_range[1] + 0.25])
    ax.set_xlim([x_range[0], x_range[1]])
    ax.set_title(title_plot)
    if chance_x:
        ax.vlines(chance_x, ymin=0, ymax=y_range[1], colors="gray", linestyles="dashed", linewidth=3)
    if chance_y:
        ax.hlines(chance_y, xmin=x_range[0], xmax=x_range[1], colors="gray", linestyles="dashed", linewidth=3)
    figure.tight_layout()
    figure.savefig(f"{title_save_file}.png", bbox_inches='tight')


def plot_multiple_bars_per_level(data_dict, x_label, title_plot, title_save_file):
    """
    Generate plot with multiple bars per level
    :param data_dict: data in dictionary format
    :param x_label: the label for the x-axis
    :param title_plot: the title of the plot
    :param title_save_file: the name of the save file
    """
    plt.cla()
    figure, ax = plt.subplots(nrows=1,
                              ncols=1,
                              figsize=(6, 7))

    n = len(data_dict.keys())
    r = np.arange(n)
    width = 0.2
    all_keys = list(data_dict.keys())
    all_value_levels = list(data_dict[all_keys[0]].keys())
    all_bars = []

    for (idx, v_level) in enumerate(all_value_levels):
        bar_temp = plt.bar(r + width * idx, [data_dict[key][v_level] for key in all_keys], width)
        all_bars.append(bar_temp)

    ax.set_xlabel(x_label)
    ax.set_ylabel("Frequency")
    ax.set_title(title_plot)

    ax.set_xticks(r + width, all_keys, rotation=90)
    ax.legend(all_bars, [f"{idx}-order puzzle" for idx in ["first", "second", "third", "fourth"]])
    figure.savefig(f"{title_save_file}.png", bbox_inches='tight')


def plot_violin(list_data, x_axis_levels, y_axis_levels, x_label, y_label, x_range, y_range, title_plot,
                title_save_file, vertical, rotation_x=0, rotation_y=0):
    """
    Generate violin plot
    :param list_data: data in list format
    :param x_axis_levels: levels on the x-axis
    :param y_axis_levels: levels on the y-axis
    :param x_label: the label for the x-axis
    :param y_label: the label for the y-axis
    :param x_range: range of values on the x-axis
    :param y_range: range of values on the y-axis
    :param title_plot: the title of the plot
    :param title_save_file: the name of the save file
    :param vertical: if True, then creates vertical violin plots, otherwise horizontal
    :param rotation_x: degree of rotation of the labels on the x-axis
    :param rotation_y: degree of rotation of the labels on the y-axis
    """
    plt.cla()
    figure, ax = plt.subplots(nrows=1,
                              ncols=1,
                              figsize=(6, 1.75))

    if vertical:
        ax.violinplot(list_data, list(range(len(x_axis_levels))), vert=vertical, showmeans=True, showextrema=True)
    else:
        ax.violinplot(list_data, list(range(len(y_axis_levels))), vert=vertical, showmeans=True, showextrema=True)
    ax.tick_params(axis='x', rotation=rotation_x)
    ax.tick_params(axis='y', rotation=rotation_y)

    if x_axis_levels:
        ax.set_xticks(list(range(len(x_axis_levels))))
        ax.set_xticklabels(x_axis_levels)
    if y_axis_levels:
        ax.set_yticks(list(range(len(y_axis_levels))))
        ax.set_yticklabels(y_axis_levels)
    ax.set_title(title_plot)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    if x_range:
        ax.set_xlim([x_range[0], x_range[1]])
    if y_range:
        ax.set_ylim([y_range[0], y_range[1]])
    figure.savefig(f"{title_save_file}.png", bbox_inches='tight')


if __name__ == '__main__':
    pass


