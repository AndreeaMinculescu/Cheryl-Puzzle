from utilities import Month, format_text_states
from formula import NOT, KNOW, PropositionalAtom
import networkx as nx


class Puzzle:
    def __init__(self, list_players, visibility, level=None):
        """
        Class that stores information regarding the design of the puzzle
        """
        # define states
        self.states_lev_one = [(Month.May, 15), (Month.May, 16), (Month.June, 17), (Month.June, 18),
                               (Month.July, 14), (Month.July, 16), (Month.August, 14), (Month.August, 17),
                               (Month.Sept, 16), (Month.Sept, 18)]
        self.states_lev_two = [(Month.May, 17), (Month.May, 18), (Month.June, 14), (Month.July, 16),
                               (Month.July, 18), (Month.August, 15), (Month.August, 16), (Month.August, 17),
                               (Month.Sept, 14), (Month.Sept, 15)]
        self.states_lev_three = [(Month.May, 15), (Month.May, 18), (Month.June, 15), (Month.June, 17),
                                 (Month.July, 14), (Month.July, 16), (Month.August, 14), (Month.August, 16),
                                 (Month.Sept, 15), (Month.Sept, 16)]
        self.states_lev_four = [(Month.May, 15), (Month.May, 18), (Month.June, 14), (Month.June, 15),
                                (Month.July, 17), (Month.July, 18), (Month.August, 16), (Month.August, 17),
                                (Month.Sept, 16), (Month.Sept, 17)]
        self.all_states = [self.states_lev_one, self.states_lev_two, self.states_lev_three, self.states_lev_four]

        # define players and their visibility
        self.players = {f"player{i}": x for i, x in enumerate(list_players)}
        self.visibility = visibility

        # compute all players' uncertainty
        self.all_uncertainty = []
        for puzzle_states in self.all_states:
            uncertainty_puzzle = []
            for player_idx in range(len(self.players)):
                uncertainty_puzzle.append(self.compute_uncertainty(player_idx, puzzle_states))
            self.all_uncertainty.append(uncertainty_puzzle)

        # define announcements
        self.announcements_lev_one = [KNOW(str(self.players["player1"]), PropositionalAtom("b"))]
        self.announcements_lev_two = [NOT(KNOW(str(self.players["player0"]), PropositionalAtom("b"))),
                                         KNOW(str(self.players["player1"]), PropositionalAtom("b"))]
        self.announcements_lev_three = [KNOW(str(self.players["player0"]),
                                                NOT(KNOW(str(self.players["player1"]), PropositionalAtom("b")))),
                                           KNOW(str(self.players["player1"]), PropositionalAtom("b"))]
        self.announcements_lev_four = [KNOW(str(self.players["player1"]), KNOW(str(self.players["player0"]),
                                                                                  NOT(KNOW(str(self.players["player1"]),
                                                                                           PropositionalAtom("b"))))),
                                          KNOW(str(self.players["player0"]), PropositionalAtom("b"))]

        self.all_announcements = [self.announcements_lev_one, self.announcements_lev_two,
                                  self.announcements_lev_three, self.announcements_lev_four]

        # define the current level of toM
        self.curr_level = level

    def set_level(self, level):
        """
        Function that updates the level of ToM of the puzzle object

        :param level: the new level of ToM
        """
        self.curr_level = level

    def compute_uncertainty(self, player_idx, possible_worlds, include_bidirectional=True, include_reflexive=True):
        """
        Given a list of worlds, computes the uncertainty (the R relation) for a player.

        Code taken and adapted from https://github.com/jdtoprug/EpistemicToMProject.

        :param player_idx: the index of the player
        :param possible_worlds: the list of worlds
        :param include_bidirectional: if True, the connection between world X and Y is counted twice (from X to Y and
        from Y to X)
        :param include_reflexive: if True, includes reflexive relations (for world X, the connection from X to X)
        :return: the uncertainty, as a list of tuples, where a tuple <X,Y> means that there is a connection from
        world X to world Y for that player
        """
        # ensure that the visibility parameter has the right shape
        if len(self.visibility) != len(self.players):
            raise IndexError("Wrong specification of self.visibilty: does not match number of players!")
        for visib in self.visibility:
            if len(visib) != len(self.players):
                raise IndexError("Wrong specification of self.visibilty: does not match number of players!")

        p_vis = self.visibility[player_idx]  # Get player 1's visibility list
        p_edges = []  # List of edges for player 1
        for pw1index in range(len(possible_worlds)):  # Loop over possible worlds 1
            pw1 = possible_worlds[pw1index]  # We want to loop over indices to construct the edges,
            # but we need the possible world itself as well
            visiblepw1 = ""  # The portion of this possible world 1 that is visible to player 1. Could be empty!
            for p2 in range(len(self.players)):  # Loop over all players 2
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
                    for p2 in range(len(self.players)):  # Same as above
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
        return p_edges

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
        num_all_states = len(self.all_states[self.curr_level])
        index = list(range(num_all_states))
        # color list: should contain at least as many colors as there are players (+1 for recursive edges)
        color_list = ['r', 'g', 'black', 'cyan', 'blue', 'yellow']

        # for each state...
        for i in range(num_all_states):
            # define the position such that the months and dates are shown in order (e.g. May on the first line,
            # June on the second line etc.)...
            x_pos = self.all_states[self.curr_level][i][1] - 14
            y_pos = self.all_states[self.curr_level][i][0].value
            # ...and add a node to the graph
            G.add_node(index[i], state=format_text_states(self.all_states[self.curr_level][i]),
                       pos=(x_pos, y_pos))

        # for each player...
        for player_idx in range(len(self.players)):
            # create edges and define color
            for edge in self.all_uncertainty[self.curr_level][player_idx]:
                # if it is a reflexive edge, then associate a unique color
                if edge[0] == edge[1]:
                    G.add_edge(edge[0], edge[1], player=self.players[f"player{player_idx}"],
                               color=color_list[len(self.players)])
                # otherwise, color code based on which player the edge is associated with
                else:
                    G.add_edge(edge[0], edge[1],
                               player=self.players[f"player{player_idx}"], color=color_list[player_idx])

        return G


if __name__ == "__main__":
    pass

