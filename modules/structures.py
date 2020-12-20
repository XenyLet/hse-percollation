import random
import itertools
from modules.utils import flatten

# SEED = 5
SEED = None

class TreeNode:
    # _active = False
    _id = None
    _cluster_label = None

    _children = []
    _parent = None
    _dist_to_root = 0

    _active = False

    def __init__(self, id: int, parent=None, children=None):
        if parent is not None:
            assert isinstance(parent, TreeNode)
        if children is not None:
            for child in children:
                assert isinstance(child, TreeNode)

        self._id = id
        # cluster_label is stored only in root node
        self._cluster_label = id

        self._parent = parent

    def __eq__(self, other):
        return self._id == other._id

    @staticmethod
    def _get_graph_nodes(node):
        cur_level_nodes = [node]
        for child in node._children:
            cur_level_nodes.extend(TreeNode._get_graph_nodes(child))
        return cur_level_nodes

    def consume_graph(self, starting_node):
        assert isinstance(starting_node, TreeNode)

        if get_root(self) == get_root(starting_node):
            return {"clusters_merged": False}

        # paths compression (all nodes in child graph should have this node as direct parent)
        target_graph_nodes = self._get_graph_nodes(starting_node)

        for child in target_graph_nodes:
            self._children.append(child)
            child._set_parent(self)
            child._children = []
            child._cluster_label = None

        return {"clusters_merged": True}

    def add_child(self, child):
        assert isinstance(child, TreeNode)

        if get_root(self) == get_root(child):
            return {"clusters_merged": False}

        self._children.append(child)
        child._set_parent(self)
        child._cluster_label = None

        return {"clusters_merged": True}

    def _set_parent(self, parent):
        assert isinstance(parent, TreeNode)

        self._parent = parent
        self._dist_to_root = self._parent.get_dist_to_root() + 1
        # if node parent is set, then this node belongs to cluster,
        #   so relevant cluster label is stored in root node,
        #   so we dont need label in this node
        self._cluster_label = None

    def get_parent(self):
        return self._parent

    def is_root(self):
        return self._parent is None

    def is_activated(self):
        return self._active

    def activate(self):
        self._active = True

    def get_id(self):
        return self._id

    def get_cluster_label(self):
        if self.is_root():
            return self._cluster_label
        else:
            get_root(self).get_cluster_label()

    def get_dist_to_root(self):
        return self._dist_to_root

class Mesh:
    _size = None
    _nodes = None
    _bonds = None
    _clusters_number = None

    HORIZONTAL = True
    VERTICAL = False

    NODES_NUM_LIMIT = 100
    TYPE_BOND = 1
    TYPE_NODE = 0

    # one builds activation sequence of bonds - order in which they will be activated later
    _random_items_gen = None

    # Class represents square mesh (k*k nodes) of nodes (N) and their connections (C)
    #
    # Mesh scheme:
    # N0 ----------C0a------------ N1 ------------C1a------------ N2 -- ... ---------C[k-2]a------- N[k-1]
    # |                            |                              |                                 |
    # C0b                          C1b                            C2b                               C[k-1]b
    # |                            |                              |                                 |
    # Nk -----------Cka----------- N[k+1] --------C[k+1]a-------- N[k+2] -- ... ------C[2k-2]------ N[2k-1]
    # |                            |                              |                                 |
    # C[k]b                        C[k+1]b                        C[k+2]b                           C[2k-1]b
    # |                            |                              |                                 |
    # ...                          ...                            ...                               ...
    # |                            |                              |                                 |
    # N[(k-1)*k] ---C[(k-1)*k]a--- N[(k-1)*k+1] --C[(k-1)*k+1]a-- N[(k-1)*k+2] -- ... --C[k^2-2]a-- N[k^2-1]
    #
    # Nodes are stored in 2-D array (self._nodes) as follows:
    #   [
    #       [N0, N1, .., Nk-1],
    #       [Nk, Nk+1, .., N2k-1],
    #       ..,
    #       [N[(k-1)*k], N[(k-1)*k+1], .., N[k^2-1]]
    #   ]
    # where Ni is an instance of class TreeNode
    #
    # Connections (bonds) are stored in form of tuples in 2-D array (self._bonds) as follows:
    #   [
    #       [(C0a, C0b), (C1a, C1b), .., (C[k-2]a, C[k-2]b), (None, C[k-1])],
    #       ...,
    #       [(None, C[k*(k-1)+1]b), (None, C[k*(k-1)+2]b), ..., (None, C[k^2-1]b), (None, None) ]
    #   ]
    # where Ci is a boolean value which indicates if connection is activated, or not. None means that there is no such connection

    def __init__(self, side_size: int, type: int):
        assert type == self.TYPE_BOND or type == self.TYPE_NODE, "Unacceptable mesh type"
        assert 0 < side_size <= self.NODES_NUM_LIMIT, "Unacceptable mesh side size"
        self._type = type

        self._size = side_size

        self._nodes = [
            [TreeNode(k * self._size + i) for i in range(self._size)] for k in range(self._size)]
        self._clusters_number = self._size ** 2

        if type == self.TYPE_BOND:
            # creating connections(bonds) matrix
            self._bonds = [[(False, False) for _ in range(self._size - 1)] for _ in
                           range(self._size - 1)]  # one needs to process last row and last column in unique way
            for bond_row in self._bonds:
                bond_row.extend([(None, False)])  # adding last column
            self._bonds.append([(False, None)] * self._size),
            self._bonds[-1][-1] = (None, None)  # fixing last element

            # creating geneator
            self._random_items_gen = self._random_bonds_generator()
        if type == self.TYPE_NODE:
            self._random_items_gen = self._random_nodes_generator()

    def _random_bonds_generator(self):
        # creating bonds activation sequence (tuples of (node_id, is_bond_horizontal)).
        #   If node is not horizontal, then it is vertical
        all_bonds = itertools.chain(
            zip(range(self._size ** 2), itertools.repeat(True, self._size ** 2)),
            zip(range(self._size ** 2), itertools.repeat(False, self._size ** 2))
        )
        # shuffling data
        all_bonds = list(all_bonds)
        if SEED:
            random.seed(SEED)
        random.shuffle(all_bonds)
        for bond in all_bonds:
            yield bond

    def _random_nodes_generator(self):
        all_nodes = [node.get_id() for node in flatten(self._nodes)]
        if SEED:
            random.seed(SEED)
        random.shuffle(all_nodes)
        for node in all_nodes:
            yield node

    def _is_node_id_ok(self, node_id):
        return 0 <= node_id < self._size ** 2

    def _is_bond_exists(self, node_id, direction: bool):
        assert self._is_node_id_ok(node_id), "Wrong node id"

        ind = self._node_id_to_indices(node_id)
        bond_tuple = self._bonds[ind[0]][ind[1]]
        if direction == self.HORIZONTAL:
            return bond_tuple[0] is not None
        else:
            return bond_tuple[1] is not None

    def _node_id_to_indices(self, node_id):
        col_ind = node_id // self._size
        row_ind = node_id % self._size
        return col_ind, row_ind

    def _indices_to_node_id(self, inds):
        col_ind, row_ind = inds
        return col_ind * self._size + row_ind

    def _get_adjacent_node_ids(self, node_id):
        inds = self._node_id_to_indices(node_id)
        displacements = [(i, k) for i, k in [(-1, 0), (1, 0), (0, 1), (0, -1)]]

        # get all indices of adjacent nodes
        tgt_indices = [(inds[0] - i, inds[1] - k) for i, k in displacements]
        # filter nodes not in bounds
        filtered_inds = [ind for ind in tgt_indices if 0 <= ind[0] < self._size and 0 <= ind[1] < self._size]

        return [self._indices_to_node_id(ind) for ind in filtered_inds]

    def _node_id_from_direction(self, start_node_id, direction: bool):
        assert self._is_node_id_ok(start_node_id), "Wrong node id"

        if self._is_bond_exists(start_node_id, direction):
            if direction == self.HORIZONTAL:
                return start_node_id + 1
            elif direction == self.VERTICAL:
                return start_node_id + self._size
        else:
            raise ValueError("Wrong direction requested")

    def _are_nodes_adjacent(self, node1_id: int, node2_id: int):
        ids_displ = abs(node1_id - node2_id)
        return ids_displ == 1 or ids_displ == self._size

    def _activate_bond(self, node_id, direction: bool):
        res = {"bond_not_exists": None,
               "bond_already_activated": None,
               "clusters_merged": None}

        assert self._is_node_id_ok(node_id), "Wrong node id"
        if not self._is_bond_exists(node_id, direction):
            res["bond_not_exists"] = True
            return res

        inds = self._node_id_to_indices(node_id)
        tgt_tuple = self._bonds[inds[0]][inds[1]]
        if direction == self.HORIZONTAL:
            if tgt_tuple[0]:
                res["bond_already_activated"] = True
                return res
            else:
                new_tgt_tuple_val = (True, tgt_tuple[1])
        elif direction == self.VERTICAL:
            if tgt_tuple[1]:
                res["bond_already_activated"] = True
                return res
            else:
                new_tgt_tuple_val = (tgt_tuple[0], True)
        else:
            raise ValueError("Incorrect argument passed: is_horizontal = {}".format(direction))

        self._bonds[inds[0]][inds[1]] = new_tgt_tuple_val

        combine_res = self._combine_clusters([node_id,
                                              self._node_id_from_direction(node_id, direction)])
        res["clusters_merged"] = combine_res["clusters_merged"]
        return res

    @staticmethod
    def _compress_path(node: TreeNode):
        nodes_travelled = []

        cur_node = node
        while cur_node is not None:
            tmp = cur_node.get_parent()
            if tmp is None:
                root_node = cur_node
            else:
                nodes_travelled.append(cur_node)

            cur_node = cur_node.get_parent()

        for node in nodes_travelled:
            node._parent = root_node

    def _combine_clusters(self, node_ids_list):
        nodes = [self.get_node(node_id) for node_id in node_ids_list]
        merged_clusters = 0

        for node in nodes:
            Mesh._compress_path(node)

        nodes_roots = [get_root(node) for node in nodes]
        root_0 = nodes_roots[0]
        for root in nodes_roots[1:]:
            if root_0.add_child(root)["clusters_merged"]:
                merged_clusters += 1

        return {"clusters_merged": merged_clusters}

    def get_node(self, node_id: int):
        assert self._is_node_id_ok(node_id), "Wrong node id"

        inds = self._node_id_to_indices(node_id)
        return self._nodes[inds[0]][inds[1]]

    def all_nodes(self):
        return self._nodes

    def all_bonds(self):
        return self._bonds

    def activate_next_random_connection(self):
        try:
            next_connection = next(self._random_items_gen)
        except StopIteration:
            return None

        res = self._activate_bond(next_connection[0], next_connection[1])

        res["next_connection"] = next_connection
        if res["clusters_merged"]:
            self._reduce_clusters_num()
            if self._clusters_number == 1:
                res["one_cluster_left"] = True

        return res

    def activate_next_random_node(self):
        try:
            next_node_id = next(self._random_items_gen)
        except StopIteration:
            return None
        next_node = self.get_node(next_node_id)
        next_node.activate()
        adjacent_active_nodes_ids = [_id for _id in self._get_adjacent_node_ids(next_node.get_id()) if
                                     self.get_node(_id).is_activated()]
        self._combine_clusters([next_node_id] + adjacent_active_nodes_ids)

    def get_size(self):
        return self._size

    def _reduce_clusters_num(self):
        self._clusters_number -= 1

    def check_percollation(self):
        # checking up-to-down-percollation
        upper_nodes_ids = range(self._size)
        max_n = self._size ** 2
        lower_nodes_ids = range(max_n - self._size, max_n)
        for u in upper_nodes_ids:
            for l in lower_nodes_ids:
                u_n, l_n = self.get_node(u), self.get_node(l)
                u_n_par, l_n_par = get_root(u_n), get_root(l_n)
                if u_n_par.get_id() == l_n_par.get_id():
                    return True
        return False

    def calculate_percollation(self):
        if self._type == self.TYPE_BOND:
            acc = 0
            for bond in flatten(self._bonds):
                acc += bond[0] if bond[0] is not None else 0
                acc += bond[1] if bond[1] is not None else 0
            return acc
        if self._type == self.TYPE_NODE:
            return sum([node.is_activated() for node in flatten(self._nodes)])

def get_root(node: TreeNode, iters_limit=Mesh.NODES_NUM_LIMIT ** 2):
    assert isinstance(node, TreeNode)

    root_search_iterations = 0

    _cur_node = node
    _par = _cur_node.get_parent()
    root_search_iterations += 1
    while _par is not None:
        _cur_node = _par
        _par = _cur_node.get_parent()
        root_search_iterations += 1
        if root_search_iterations > iters_limit:
            raise RuntimeError("Tree loop detected (more {} iterations done)".format(iters_limit))
    return _cur_node

    # if __name__ == '__main__':
    #     mesh = Mesh(5)
    #
    #     from modules.visualizer import Visualizer
    #     from time import sleep
    #
    #     v = Visualizer()
    #
    #     conn_activated = {"one_cluster_left": False}
    #
    #     while not conn_activated.get("one_cluster_left"):
    #         conn_activated = mesh.activate_next_random_connection()
    #         print(conn_activated)
    #         print(mesh._clusters_number)
    #         v.draw_mesh(mesh)
    #         sleep(1)
    #
    #     input()
