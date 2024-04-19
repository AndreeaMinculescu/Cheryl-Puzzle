from enum import Enum
import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt  # Drawing graphs
import networkx as nx


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


if __name__ == "__main__":
    pass
