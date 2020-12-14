import argparse
from random import randint
from modules.visualizer import Visualizer
from modules.structures import Mesh, TreeNode


# def activate_mesh_node(mesh, tgt_node_id):


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--sidesize", "-s", type=int, choices=range(1, 100), dest="size", required=True,
                        help="Size size of modelling mesh (square) in nodes")
    parser.add_argument("--type", "-t", type=str, choices=["BOND", "NODE"], required=True,
                        help="Type of Model (BOND or NODE)")
    parser.add_argument("--pause", "-p", type=float, default=1, help="Pause between nodes/bonds activation")
    args = parser.parse_args()



    mesh = Mesh(args.size, Mesh.TYPE_BOND if args.type=="BOND" else Mesh.TYPE_NODE)

    from modules.visualizer import Visualizer
    from time import sleep


    v = Visualizer(Mesh.TYPE_BOND if args.type == "BOND" else Mesh.TYPE_NODE)

    conn_activated = {"one_cluster_left": False}

    while not mesh.check_percollation():
        if args.type=="BOND":
            mesh.activate_next_random_connection()
        if args.type =="NODE":
            mesh.activate_next_random_node()
        # print(conn_activated)
        # print(mesh._clusters_number)
        v.draw_mesh(mesh)
        sleep(args.pause)

    print("Bond percollation: ", mesh.calculate_percollation())
    input("Press any key to quit")

