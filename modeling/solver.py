import random
from utilities import format_text_states
import networkx as nx

SEED = 42


class Solver:
    def __init__(self, max_iter, max_tom_level, curr_tom_level, puzzle):
        """
        Class that stores all elements common to all solvers
        """
        # store the maximum number of model iterations per ToM level
        self.max_iter = max_iter
        # store the maximum number of ToM levels
        self.max_tom_level = max_tom_level
        # store the current ToM level
        self.curr_level = curr_tom_level
        # store the current puzzle object
        self.puzzle = puzzle

        # compute all players' uncertainty
        self.all_uncertainty = None
        self.init_graph = self.generate_full_model()

    def run_model_once(self, **kwargs):
        """
        All models that inherit from Solver must have a run_model_once function implemented
        """
        raise NotImplementedError

    def compute_uncertainty(self, include_bidirectional=True, include_reflexive=True):
        """
        Given a list of worlds, computes the uncertainty (the R relation) for a player.

        Code taken and adapted from https://github.com/jdtoprug/EpistemicToMProject.

        :param include_bidirectional: if True, the connection between world X and Y is counted twice (from X to Y and
        from Y to X)
        :param include_reflexive: if True, includes reflexive relations (for world X, the connection from X to X)
        :return: the uncertainty, as a list of tuples, where a tuple <X,Y> means that there is a connection from
        world X to world Y for that player
        """
        # ensure that the visibility parameter has the right shape
        if len(self.puzzle.visibility) != len(self.puzzle.players):
            raise IndexError("Wrong specification of self.visibilty: does not match number of players!")
        for visib in self.puzzle.visibility:
            if len(visib) != len(self.puzzle.players):
                raise IndexError("Wrong specification of self.visibilty: does not match number of players!")

        all_uncertainty = []
        for possible_worlds in self.puzzle.all_states:
            uncertainty_puzzle = []
            for player_idx in range(len(self.puzzle.players)):
                for player_idx in range(len(self.puzzle.players)):
                    p_vis = self.puzzle.visibility[player_idx]  # Get player 1's visibility list
                    p_edges = []  # List of edges for player 1
                    for pw1index in range(len(possible_worlds)):  # Loop over possible worlds 1
                        pw1 = possible_worlds[pw1index]  # We want to loop over indices to construct the edges,
                        # but we need the possible world itself as well
                        visiblepw1 = ""  # The portion of this possible world 1 that is visible to player 1. Could be empty!
                        for p2 in range(len(self.puzzle.players)):  # Loop over all players 2
                            if p_vis[p2]:  # If player 1 can see this player
                                subsetp1 = pw1[p2:p2 + 1]
                                visiblepw1 += str(subsetp1)  # Add this part of
                                # the possible world
                        for pw2index in range(len(possible_worlds)):  # Loop over possible worlds 2
                            pw2 = possible_worlds[pw2index]  # Same as above
                            # pw2 = pw2.split(", ")
                            if pw1[0].value > pw2[0].value or pw1[1] < pw2[1]:  # One-directional non-reflexive edges
                                visiblepw2 = ""  # The portion of this possible world 2 that is visible to player 1. Could be
                                # empty!
                                for p2 in range(len(self.puzzle.players)):  # Same as above
                                    if p_vis[p2]:
                                        subsetp2 = pw2[p2:p2 + 1]
                                        visiblepw2 += str(subsetp2)
                                if visiblepw1 == visiblepw2:  # If two possible worlds are indistinguishable
                                    newedge = (pw1index, pw2index)  # Give this player an edge between those worlds
                                    if newedge not in p_edges:  # No duplicate edges
                                        p_edges.append(newedge)

                    if include_bidirectional:
                        p_edges += [(y, x) for (x, y) in p_edges]
                    if include_reflexive:
                        p_edges += [(x, x) for x in range(len(possible_worlds))]
                    uncertainty_puzzle.append(p_edges)
            all_uncertainty.append(uncertainty_puzzle)

        return all_uncertainty

    def update_uncertainty(self, player_idx, list_states):
        """
        After changes are made to the model, update the uncertainty for a player: remove all connections between
        states that are not part of the model anymore

        :param player_idx: the index of the player
        :param list_states: the new list of states still part of the model
        """
        initial_edges = self.all_uncertainty[self.curr_level][player_idx]
        self.all_uncertainty[self.curr_level][player_idx] = [edge for edge in initial_edges if
                                                             edge[0] in list_states and edge[1] in list_states]

    def generate_full_model(self):
        """
        Generates the full initial epistemic structure as a networkx graph

        :return: the graph
        """
        # define a directed graph
        G = nx.DiGraph()
        # get the number of states (note that the states are hardcoded in the Puzzle class)
        num_all_states = len(self.puzzle.all_states[self.curr_level])
        # compute players' uncertainty (the R relation)
        self.all_uncertainty = self.compute_uncertainty()
        index = list(range(num_all_states))
        # color list: should contain at least as many colors as there are players (+1 for recursive edges)
        color_list = ['r', 'g', 'black', 'cyan', 'blue', 'yellow']

        # for each state...
        for i in range(num_all_states):
            # define the position such that the months and dates are shown in order (e.g. May on the first line,
            # June on the second line etc.)...
            x_pos = self.puzzle.all_states[self.curr_level][i][1] - 14
            y_pos = self.puzzle.all_states[self.curr_level][i][0].value
            # ...and add a node to the graph
            G.add_node(index[i], state=format_text_states(self.puzzle.all_states[self.curr_level][i]),
                       pos=(x_pos, y_pos), node_color="white")

        # for each player...
        for player_idx in range(len(self.puzzle.players)):
            # create edges and define color
            for edge in self.all_uncertainty[self.curr_level][player_idx]:
                # if it is a reflexive edge, then associate a unique color
                if edge[0] == edge[1]:
                    G.add_edge(edge[0], edge[1], player=self.puzzle.players[f"player{player_idx}"],
                               color=color_list[len(self.puzzle.players)])
                # otherwise, color code based on which player the edge is associated with
                else:
                    G.add_edge(edge[0], edge[1],
                               player=self.puzzle.players[f"player{player_idx}"], color=color_list[player_idx])

        return G

if __name__ == "__main__":
    pass