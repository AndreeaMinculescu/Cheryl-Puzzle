from enum import Enum
import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt  # Drawing graphs
import networkx as nx
from collections import Counter


class Month(Enum):
    May = 4
    June = 3
    July = 2
    August = 1
    Sept = 0


def format_text_states(state):
    """
    Transforms a state's description from e.g. <Month.May, 15> to "May, 15"

    :return: the formatted description
    """
    return f'{state[0].name}, {str(state[1])}'


def get_common_ratio(model_answers, subj_answers):
    """
    Computes the percentage of participant data explained by the model as:
        the number of common answers / total number of answers

    :param model_answers: list of answers given by the model
    :param subj_answers: list of answers given by the participants
    :return: percentage of explained data
    """
    # for consistency across answers, replace all occurrences of "Sept" with "September"
    model_answers = [date.replace("Sept", "September") for date in model_answers]
    model_dict = dict(Counter(model_answers))
    subj_dict = dict(Counter(subj_answers))
    # keep track of the common answers
    common_keys = list(set(model_dict.keys()).intersection(subj_dict.keys()))
    # count how many occurrences of the common answers exist
    common_values = sum([min(model_dict[key], subj_dict[key]) for key in common_keys])
    return common_values * 100 / len(subj_answers)


def draw_model(graph, save_file=None):
    """
    Draws a graph and possibly saves to file

    :param graph: the graph to be drawn
    :param save_file: the path to save the file
    """
    # define figure size
    fgsz = 7

    # create empty drawing area
    plt.figure(1, figsize=(fgsz, fgsz))
    # remove most margins
    plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)

    # retrieve the position of each node relative to the others
    pos = nx.get_node_attributes(graph, 'pos')
    # retrieve the label for each state
    state_labels = nx.get_node_attributes(graph, 'state')
    # retrieve the color for each edge
    edge_color = nx.get_edge_attributes(graph, 'color')
    # retrieve the label for each edge
    edge_labels = nx.get_edge_attributes(graph, 'player')

    # draw the nodes and edges
    nx.draw(graph, pos, node_size=3750, node_color="white", font_size=10, font_weight='bold',
            labels=state_labels, with_labels=True, edge_color=edge_color.values(), edgecolors="black")

    # display the edge colors and labels
    [nx.draw_networkx_edge_labels(graph, pos, edge_labels={i: e}, font_color=edge_color[i],
                                  font_size=10, rotate=False)
     for i, e in edge_labels.items()]

    # if a file path was given, then save the drawing as a png file
    if save_file:
        plt.savefig(f"{save_file}.png")
    # otherwise, show the drawing
    else:
        plt.show()

    # clear plot
    plt.clf()

def plot_bar(data, title_plot, x_label, y_label, y_range, x_range, title_save_file=None, chance_x=None, chance_y=None,
             rotation_x=90, rotation_y=0, bar_width=0.8):
    """
    Generate simple bar plot
    :param data: data in dictionary format
    :param title_plot: the title of the plot
    :param x_label: the label for the x-axis
    :param y_label: the label for the y-axis
    :param title_save_file: the name of the save file
    :param rotation_x: degree of rotation of the labels on the x axis
    """
    plt.cla()
    figure, ax = plt.subplots(nrows=1,
                              ncols=1,
                              figsize=(5, 7))
    ax.bar(list(data.keys()), list(data.values()), edgecolor='black', width=bar_width)
    ax.set_xlabel(x_label)
    ax.tick_params(axis='x', rotation=rotation_x)
    ax.tick_params(axis='y', rotation=rotation_y)
    ax.set_xticks(list(data.keys()))
    ax.set_ylabel(y_label)
    ax.set_yticks(list(data.values()))
    ax.set_ylim([y_range[0], y_range[1]])
    ax.set_title(title_plot)
    if chance_x:
        ax.vlines(chance_x, ymin=0, ymax=y_range[1], colors="gray", linestyles="dashed", linewidth=3)
    if chance_y:
        ax.hlines(chance_y, xmin=x_range[0], xmax=x_range[1], colors="gray", linestyles="dashed", linewidth=3)
    figure.tight_layout()
    if title_save_file:
        figure.savefig(f"{title_save_file}.png", bbox_inches='tight')
    else:
        figure.show()



if __name__ == "__main__":
    pass
