import argparse
from modules.structures import Mesh
from modules.visualizer import Visualizer
from time import sleep



# def activate_mesh_node(mesh, tgt_node_id):

def conduct_experiment(mesh_size, mesh_type, visualize=False, pause=0.1):
    mesh = Mesh(mesh_size, mesh_type)

    if visualize:
        v = Visualizer(mesh_type)

    while not mesh.check_percollation():
        if mesh_type == Mesh.TYPE_BOND:
            mesh.activate_next_random_connection()
        if mesh_type == Mesh.TYPE_NODE:
            mesh.activate_next_random_node()
        if visualize:
            v.draw_mesh(mesh)
            sleep(pause)

    if visualize:
        del v
    return mesh_size, mesh_type, mesh.calculate_percollation()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--sidesize", "-s", type=int, dest="size", required=True,
                        help="Size size of modelling mesh (square) in nodes")
    parser.add_argument("--type", "-t", type=str, choices=["BOND", "NODE"], required=True,
                        help="Type of Model (BOND or NODE)")
    parser.add_argument("--pause", "-p", type=float, default=1, help="Pause between nodes/bonds activation")
    parser.add_argument("--vis", action="store_true", help="Show mesh visualization")
    args = parser.parse_args()

    assert 50 >= args.size >= 1, "Mesh size should be integer in [1; 50]"
    assert args.pause > 0, "Pause should be > 0"

    res = conduct_experiment(args.size,
                             Mesh.TYPE_BOND if args.type == "BOND" else Mesh.TYPE_NODE,
                             args.vis,
                             args.pause)

    print("Experiment finished!")
    print("Items activated: {}".format(res[2]))
    input("Press any key to quit")