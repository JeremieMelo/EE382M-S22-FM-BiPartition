"""
Description:
Author: Jiaqi Gu (jqgu@utexas.edu)
Date: 2022-01-21 17:27:54
LastEditors: Jiaqi Gu (jqgu@utexas.edu)
LastEditTime: 2022-01-21 20:21:53
"""
import time
from typing import List, Tuple

import memory_profiler as mp
import numpy as np

#############################################
# This is the base class for FM partition
# Please do not change any code in this file
#############################################


class FM_Partition_Base(object):
    def __init__(self) -> None:
        super().__init__()
        # net to node map: array of array
        # e.g., net2node_map[i] is a list that contains all node indices in the net i, where i is the net index
        self.net2node_map = None
        self.n_nets = 0
        self.n_nodes = 0
        self.min_cut_ratio_epsilon = 1e-5

    # Please do not override the method
    def read_graph(self, file_path: str) -> Tuple[List[List[str]], int, int]:
        """Read graph from file_path

        Args:
            file_path (str): path to the graph description file

        Returns:
            Tuple[List[List[int]], int, int]: array of nets (net to node map), number of nets, number of nodes
        """
        with open(file_path, "r") as f:
            lines = f.readlines()
            self.n_nodes = int(lines[0].strip())
            self.n_nets = int(lines[1].strip())
            # The raw graph is described as a net to node names map
            self.net2node_name_map = [[i for i in line.strip().split(" ")[1:]] for line in lines[2:-1]]
            self.min_cut_ratio = float(lines[-1].strip())

            # We sort the node names and assign each node an index
            # We create a map from node index to node name. This is an array.
            node_name_list = []
            for node_names in self.net2node_name_map:
                node_name_list.extend(node_names)
            self.node_names = set(node_name_list)
            self.node2node_name_map = np.array(sorted(self.node_names))

            # We also need a map from node name to node index. This is a hash map
            self.node_name2node_map = {}
            for node, node_name in enumerate(self.node2node_name_map):
                self.node_name2node_map[node_name] = node

            # Finally we need a map from net to node indices. This is an array of variable-length array
            net2node_map = []
            for node_names in self.net2node_name_map:
                net2node_map.append([self.node_name2node_map[name] for name in node_names])
            self.net2node_map = net2node_map

            assert (
                len(self.net2node_map) == self.n_nets
            ), f"There are {self.n_nets} nets, but only {len(self.net2node_map)} nets are parsed."
        return self.net2node_map, self.n_nets, self.n_nodes

    def initialize(self):
        """Initialize necessary data structures before starting solving the problem"""
        raise NotImplementedError

    def partition_one_pass(self) -> Tuple[List[int], Tuple[List[str], List[str]], int]:
        """FM graph partition algorithm for one pass

        Return:
            cut_size_list (List[int]): contains the initial cut size and the cut size after each move
            best_sol (Tuple[List[str], List[str]]): The best partition solution is a tuple of two blocks. Each block is a list of the given node names
            best_cut_size (int): The cut size corresponding to the best partition solution
        """
        raise NotImplementedError

    # Please do not override the method
    def solve(self) -> Tuple[List[int], Tuple[List[str], List[str]], int]:
        self.initialize()
        return self.partition_one_pass()

    # Please do not override the method
    def verify_solution(self, sol: Tuple[List[int], List[int]]) -> bool:
        p0, p1 = sol
        n_nodes = self.n_nodes
        if not (
            all(n in self.node_names for n in p0) and
            all(n in self.node_names for n in p1)
        ):
            print(f"There is invalid node in the solution")
            return False

        if len(p0) + len(p1) != self.n_nodes:
            print(f"The solution contains {len(p0) + len(p1)} nodes != total {self.n_nodes} nodes")
            return False

        p = set(list(p0) + list(p1))
        if len(p) < len(p0) + len(p1):
            print(f"Duplicate nodes appear in the solution")
            return False

        cut_ratio = min(len(p0), len(p1)) / n_nodes
        if cut_ratio < self.min_cut_ratio - self.min_cut_ratio_epsilon:
            print(f"cut ratio {cut_ratio} is smaller than min cut ratio {self.min_cut_ratio}")
            return False

        return True

    # Please do not override the method
    def compute_cut_size(self, sol: Tuple[List[int], List[int]]) -> int:
        net2node = self.net2node_map
        p0 = set(sol[0])

        cut_size = 0
        for net in range(self.n_nets):
            nodes = net2node[net]
            flags = [n in p0 for n in nodes]
            if not all(flags) and any(flags):
                cut_size += 1
        return cut_size

    # Please do not override the method
    def profile(self, n_runs: int = 10) -> Tuple[float, float]:
        runtime = 0
        for _ in range(n_runs):
            start = time.time()
            self.solve()
            end = time.time()
            runtime += end - start
        runtime /= n_runs

        start_mem = mp.memory_usage(max_usage=True)
        res = mp.memory_usage(proc=(self.solve, []), max_usage=True, retval=True)
        max_mem = res[0]
        used_mem = max_mem - start_mem
        return runtime, used_mem

    # Please do not override the methods
    def dump_output_file(
        self,
        cut_size_list: List[int],
        best_sol: Tuple[List[str], List[str]],
        best_cut_size: int,
        runtime: float,
        used_mem: float,
        output_path: str,
    ) -> None:
        with open(output_path, "w") as f:
            output = (
                " ".join(map(str, cut_size_list))
                + "\n"
                + " ".join(map(str, best_sol[0]))
                + "\n"
                + " ".join(best_sol[1])
                + "\n"
                + str(best_cut_size)
                + "\n"
                + str(runtime)
                + "\n"
                + str(used_mem)
            )
            f.write(output)

    # Please do not override the methods
    def load_solution(self, output_path: str):
        with open(output_path, "r") as f:
            lines = f.readlines()
            cut_size_list = [int(i) for i in lines[0].strip().split(" ")]
            p0 = lines[1].strip().split(" ")
            p1 = lines[2].strip().split(" ")
            solution = [p0, p1]
            min_cut_size = int(lines[3].strip())
            runtime = float(lines[4].strip())
            used_mem = float(lines[5].strip())
        return cut_size_list, solution, min_cut_size, runtime, used_mem
