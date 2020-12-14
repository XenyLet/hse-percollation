from tkinter import Tk, Canvas, LAST as TK_LAST, FIRST as TK_FIRST
from math import cos, sin, atan, pi
from collections import namedtuple

from modules.structures import Mesh, TreeNode
from modules.utils import flatten


class Visualizer:
    MIN_NODE_SIZE = (20, 20)
    MIN_CONN_LEN = 20

    WIN_SIZE = (500, 500)

    TYPE_BOND = 1
    TYPE_NODE = 0

    def __init__(self, _type):
        assert _type == Visualizer.TYPE_BOND or _type == Visualizer.TYPE_NODE, "Wrong Visualizer type"

        self._type = _type
        # super().__init__()
        self._root = Tk()

        self._canvas = Canvas(self._root,
                              width=self.WIN_SIZE[0],
                              height=self.WIN_SIZE[1],
                              bg='white')
        self._canvas.pack()

    @staticmethod
    def _get_circle_radius(cell_size):
        return cell_size / 4

    @staticmethod
    def _get_circle_point(circle_radius, center_x, center_y, angle_rad):
        return center_x + circle_radius * cos(angle_rad), \
               center_y + circle_radius * sin(angle_rad)

    @staticmethod
    def _get_circles_intersections_with_centers_line(circle_radius, center1_x, center1_y, center2_x, center2_y):
        Point = namedtuple("Point", ["x", "y"])

        p1 = Point(center1_x, center1_y)
        p2 = Point(center2_x, center2_y)

        ps_sorted = sorted([p1, p2], key=lambda x: (x[0], x[1]))
        points_were_reversed = p1 != ps_sorted[0]
        p1, p2 = ps_sorted[0], ps_sorted[1]

        if p1.x - p2.x == 0:
            angle1_rad = pi / 2
            angle2_rad = -pi / 2
        elif p1.y - p2.y == 0:
            angle1_rad = 0
            angle2_rad = -pi
        else:
            angle1_rad = atan((p2.y - p1.y) / (p2.x - p1.x))
            angle2_rad = pi + angle1_rad
        return points_were_reversed, \
               Visualizer._get_circle_point(circle_radius, p1.x, p1.y, angle1_rad), \
               Visualizer._get_circle_point(circle_radius, p2.x, p2.y, angle2_rad)

    def _size(self):
        # canvas = Canvas(self)
        # w = canvas.winfo_width()
        # h = canvas.winfo_height()
        return self.WIN_SIZE

    def _get_anchors(self, anchors_num_w, anchors_num_h):
        one_node_widht = self._size()[0] / anchors_num_w
        one_node_height = self._size()[1] / anchors_num_h

        assert one_node_widht > self.MIN_NODE_SIZE[0] + self.MIN_CONN_LEN / 2 \
               and one_node_height > self.MIN_NODE_SIZE[1] + self.MIN_CONN_LEN / 2, \
            "Canvas is too small for all nodes to be drawn. Current size of one node and halfs of it's connections: {} x {}" \
                .format(one_node_widht, one_node_height)

        side_size = min(one_node_height, one_node_widht)

        displ = [0, 0]  # x (width), y (height)
        nodes_anchors = []
        while displ[1] < self._size()[1] - side_size / 2:
            while displ[0] < self._size()[0] - side_size / 2:
                nodes_anchors.append((displ[0] + side_size / 2, displ[1] + side_size / 2))
                displ[0] += side_size
            displ[0] = 0
            displ[1] += side_size

        return side_size, nodes_anchors

    def _draw_nodes(self, nodes: list, cell_size, anchors, add_ids=False):
        # for node_row in nodes:
        #     for node in node_row:
        #         assert type(node) == TreeNode, "Wrong node type: {}".format(type(node))

        circle_radius = self._get_circle_radius(cell_size)

        for anchor, node in zip(anchors, flatten(nodes)):
            center_x = anchor[0]
            center_y = anchor[1]
            self._canvas.create_oval(
                center_x - circle_radius, center_y - circle_radius,
                center_x + circle_radius, center_y + circle_radius,
                outline="green" if node.is_activated() else "red"
            )
            if add_ids:
                self._canvas.create_text(center_x, center_y, text=str(node.get_id()))
                self._canvas.create_text(center_x, center_y + circle_radius / 2, text=node.get_cluster_label(),
                                         fill="red")

    def _draw_connections(self, connections, cell_size, anchors):
        circle_radius = self._get_circle_radius(cell_size)
        connection_len = cell_size - circle_radius * 2

        for connection, anchor in zip(flatten(connections), anchors):
            colors = {
                True: "green",
                False: "white"
            }

            width = 2

            if connection[0] is not None:
                # draw horizontal line
                self._canvas.create_line(anchor[0] + circle_radius, anchor[1],
                                         anchor[0] + circle_radius + connection_len, anchor[1],
                                         fill=colors[connection[0]], width=width)
            if connection[1] is not None:
                # draw vertical line
                self._canvas.create_line(anchor[0], anchor[1] + circle_radius,
                                         anchor[0], anchor[1] + circle_radius + connection_len,
                                         fill=colors[connection[1]], width=width)

    def _draw_tree_connections(self, nodes: list, cell_size, anchors):
        # for node_row in nodes:
        #     for node in node_row:
        #         assert isinstance(node, TreeNode), "Wrong node type: {}".format(type(node))

        circle_radius = self._get_circle_radius(cell_size)

        iter_list = list(zip(anchors, flatten(nodes)))

        for anchor, node in iter_list:
            par = node.get_parent()
            if par is None:
                continue
            node_parent_id = par.get_id()
            parent_anchor = iter_list[node_parent_id][0]
            points_were_reversed, p1, p2 = Visualizer._get_circles_intersections_with_centers_line(circle_radius,
                                                                                                   anchor[0], anchor[1],
                                                                                                   parent_anchor[0],
                                                                                                   parent_anchor[1])
            if not points_were_reversed:
                arrow = TK_LAST
            else:
                arrow = TK_FIRST
            self._canvas.create_line(p1[0], p1[1], p2[0], p2[1], arrow=arrow)

    def draw_mesh(self, mesh: Mesh, add_ids=True):
        self._canvas.delete("all")

        nodes = mesh.all_nodes()
        bonds = mesh.all_bonds()
        cell_size, anchors = side_size, anchors = self._get_anchors(len(nodes[0]), len(nodes))
        self._draw_nodes(nodes, cell_size, anchors, add_ids=add_ids)
        if self._type == Visualizer.TYPE_BOND:
            self._draw_connections(bonds, cell_size, anchors)
        self._draw_tree_connections(nodes, cell_size, anchors)

        self._root.update()


if __name__ == '__main__':
    v = Visualizer()
    v.draw_mesh(Mesh(5))
    v.start_ui()
