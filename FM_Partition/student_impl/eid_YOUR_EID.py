#######################################################################
# Implementation of FM partition
# You need to implement initialize() and partition_one_pass()
# All codes should be inside FM_Partition class
# Name:
# UT EID:
#######################################################################

from typing import List, Tuple

import numpy as np

from .p1_partition_base import FM_Partition_Base

__all__ = ["FM_Partition"]

class FM_Partition(FM_Partition_Base):
    def __init__(self) -> None:
        super().__init__()

    def initialize(self):
        """Initialize necessary data structures before starting solving the problem
        """
        self.cut_size = 0
        # TODO initial solutions: block 0 and block 1
        # To ensure a deterministic solution, use the following partition as the initial solution
        # sort the node names in alphabetical order
        # the first floor(N/2) nodes are in the first partition, The rest N-floor(N/2) nodes are in the second partition
        # a_0, a_1, ..., a_N/2-1 | a_N/2, a_N/2+1, ..., a_N-1, if N even
        # a_0, a_1, ..., a_(N-3)/2 | a_(N-1)/2, ..., a_N-1, if N odd
        # ...

        # TODO initialize any auxiliary data structure you need
        # e.g., node2net_map, cell gains, locked cells, etc.
        raise NotImplementedError

    def partition_one_pass(self) -> Tuple[List[int], Tuple[List[str], List[str]], int]:
        """FM graph partition algorithm for one pass

        Return:
            cut_size_list (List[int]): contains the initial cut size and the cut size after each move
            best_sol (Tuple[List[str], List[str]]): The best partition solution is a tuple of two blocks. Each block is a list of node names. (Please use the original node names from the benchmark file. Hint: you might need to use node2node_name_map). If multiple solutions have the best cut size, return the first one.
            best_cut_size (int): The cut size corresponding to the best partition solution
        """
        # TODO implement your FM partition algorithm for one pass.
        # To make this method clean, you can extract subroutines as methods of this class
        # But do not override methods in the parent class
        # Please strictly follow the return type requirement.

        raise NotImplementedError
