import multiprocessing
import time
from itertools import groupby
from main import conduct_experiment
from modules.structures import Mesh

import matplotlib.pyplot as plt
from numpy import polyfit


def calculate_value_from_polynom_coeffs(coeffs: list, x):
    deg = 0
    res = 0
    for coeff in reversed(coeffs):
        res += coeff * x ** deg
        deg += 1
    return res


def construct_args_list_for_experiment_set():
    mult_mesh_sizes = EXPERIMENTS_PER_SIZE * 2
    mult_mesh_type = EXPERIMENTS_PER_SIZE * len(MESH_SIZES)
    return (
        zip(
            MESH_SIZES * mult_mesh_sizes,
            [Mesh.TYPE_NODE] * mult_mesh_type + [Mesh.TYPE_BOND] * mult_mesh_type
        )
    )


def get_results_for_type(avg_results, _type):
    return list(map(
        lambda res: res[1],
        filter(
            lambda res: res[0][0] == _type,
            avg_results)
    ))


def get_avg_percollations_not_cool():
    avg_percollations = {}
    for t in [Mesh.TYPE_BOND, Mesh.TYPE_NODE]:
        print("Type {} experiments start ()".format(t, EXPERIMENTS_PER_SIZE))
        avg_percollations[t] = []
        for mesh_size in MESH_SIZES:
            print("Mesh size {} exp set start".format(mesh_size))
            start = time.time()
            cur_percollations = []
            for _ in range(EXPERIMENTS_PER_SIZE):
                cur_percollations.append(
                    conduct_experiment(mesh_size, t)
                )
            avg_percollations[t].append(
                sum(cur_percollations) / len(cur_percollations)
            )
            print("Mesh size {} exp set end. "
                  "avg perc: {}. time taken ()".format(mesh_size,
                                                       avg_percollations[t][-1],
                                                       time.time() - start))
    return avg_percollations


def get_avg_percollations_cool():
    print("Starting experiments in multiprocessing mode"
          "\n\tProcesses_number: {}".format(PROCESSES))
    start = time.time()
    with multiprocessing.Pool(processes=PROCESSES) as pool:
        results = pool.starmap(
            conduct_experiment,
            construct_args_list_for_experiment_set()
        )

    results_key = lambda x: (x[1], x[0])
    avg_results = [
        (
            key,
            sum([i[2] for i in values]) / EXPERIMENTS_PER_SIZE
        )
        for key, values in
        groupby(
            sorted(
                results,
                key=results_key
            ),
            key=results_key)
    ]

    avg_percollations = {
        Mesh.TYPE_BOND: get_results_for_type(avg_results, Mesh.TYPE_BOND),
        Mesh.TYPE_NODE: get_results_for_type(avg_results, Mesh.TYPE_NODE),
    }
    print("\tAll experiments were conducted! Time taken: {:.2f}s".format(time.time() - start))
    return avg_percollations


if __name__ == '__main__':
    MESH_SIZES = list(range(5, 41, 5))
    EXPERIMENTS_PER_SIZE = 1
    PROCESSES = 6
    GUESS_POLYNOM_DEGREE = 2

    print("Start experiments."
          "\n\tAim:\n\t\tMesh sizes: {}"
          "\n\t\tExperiments per mesh size: {}".format(list(MESH_SIZES),
                                                       EXPERIMENTS_PER_SIZE))

    avg_percollations = get_avg_percollations_cool()

    plt.figure()
    plt.plot(MESH_SIZES, avg_percollations[Mesh.TYPE_BOND], 'go', label='Bond perc. experiment')
    plt.plot(MESH_SIZES, avg_percollations[Mesh.TYPE_NODE], 'bo', label='Node perc. experiment')

    print("Trying to fit points with Polynomial curve with a degree of 2")
    coeffs_bond = polyfit(MESH_SIZES, avg_percollations[Mesh.TYPE_BOND], GUESS_POLYNOM_DEGREE)
    coeffs_node = polyfit(MESH_SIZES, avg_percollations[Mesh.TYPE_NODE], GUESS_POLYNOM_DEGREE)
    print("\tFound coeffs: \n"
          "\t\tBond: {}\n"
          "\t\tNode: {}".format(coeffs_bond, coeffs_node))

    plt.plot(MESH_SIZES,
             [calculate_value_from_polynom_coeffs(coeffs_bond, mesh_size) for mesh_size in MESH_SIZES],
             'g-',
             label='Bond perc. guess'
             )
    plt.plot(MESH_SIZES,
             [calculate_value_from_polynom_coeffs(coeffs_node, mesh_size) for mesh_size in MESH_SIZES],
             'b-',
             label='Node perc. guess'
             )

    plt.legend(loc="lower right")
    plt.title("Percollation VS Mesh side size")
    plt.xlabel("Mesh side size")
    plt.ylabel("Avg. activated items (nodes/bonds) number")
    plt.show()

    input()
