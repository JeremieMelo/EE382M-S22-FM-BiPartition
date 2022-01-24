# Coding Assignment 1: Fiduccia-Mattheyses (FM) BiPartition
Implement one pass of the FM bipartition algorithm for hypergraphs on CPU.

# Recommended Python Environment
 * Python >= 3.6.6
 * Numpy >= 1.17.0
   * Install with this command: `pip3 install numpy`
 * memory_profiler >= 0.60.0
   * Install with this command: `pip3 install memory-profiler psutil`

# Codebase Structure
 - FM_Partition
   * `benchmarks`: text-based hypergraph benchmarks
     * e.g., example_1.txt
     ```bash
        10
        8
        n0 a9 a8
        n1 a9 a1
        n2 a7 a1 a4 a0 a5
        n3 a10 a5
        n4 a10 a8
        n5 a8 a1 a3
        n6 a8 a4 a1 a6 a10
        n7 a6 a7
        0.35
     ```
     * The first row contains the number of nodes (|V|), e.g., here is 10.
     * The second row contains the number of nets/hyperedges (|E|), e.g., here is 8.
     * There are |E| rows, e.g. here is 8, starting from the third row. Each row follows the format:
     ```bash
     NET_NAME NODE_NAME_1 NODE_NAME_2 ... NODE_NAME_K
     ```
     E.g., `n5 a8 a1 a3` describs a `3-pin` net named `n5` which connects three nodes, i.e., `a8`, `a1`, and `a3`.
     * The last row is the minimum cut ratio constraint `r`. A legal bipartition [P0, P1] should satisfy `min(|P0|, |P1|)/(|V|) >= r - epsilon`, where the margin epsilon = 1e-5.
    * `output`: directory to dump out your partition solution.
      * For a student with EID: `xxxxx`, all solution files will be dumped to `output/xxxxx/`. The solution file will have the same file name as the benchmark file, e.g., `output/xxxxx/example_1.txt`
      * `output/reference`: contains ground truth solutions to the example benchmarks given to you.
      * The format of the bipartition solution file is as follows,
      ```bash
          6 4 4 3 3 3 4 5 6 5 6
          a0 a1 a3 a4 a8 a9
          a10 a5 a6 a7
          3
          0
          0
      ```
      * The first row is the cut size list which contains the initial cut size and the cut size after each move.
      * The second and third rows record the FIRST best bipartition solution with the minimum cut size.
        * The second row contains the node names in the first partition (P0) (order of the nodes does not matter).
        * The third row contains the node names in the second partition (P1) (order of the nodes does not matter).
      * The fourth row contains the min cut size corresponding to the best solution
      * The fifth row is the average runtime in second (Can ignore this, just put a 0 there)
      * The last row is the used memory (Can ignore this, just put a 0 there)
    * `student_impl`: directory to store algorithm implementations.
      * `__init__.py`: initialize package.
      * `p1_partition_base.py`: basic class of the FM partition solver `FM_Partition_Base`. Please do not change any code in this file.
      * `eid_YOUR_EID.py`: `FM_Partition` class inherited from `FM_Partition_Base`.
        * The first thing you need to do is to replace `YOUR_EID` in the file name with your lowercase UT EID, e.g., eid_xxxxx.py.
        * **You need to implement the `initialize()` and `partition_one_pass()` methods**.
        * Please keep all codes within the `FM_Partition` class.
        * Please only submit this single file. Any codes outside `FM_Partition` class or outside this file will be ignored.
        * A reasonable amount of comments are encouraged to improve the code readability.
    * `p1_partition_eval.py`: script to evaluate your partition solver on given benchmarks.
      * Below is an example to perform evaluation for `YOUR_UT_EID`, e.g., `xxxxx`, on `BENCHMARK_PATH`, e.g., `./benchmarks/example_1.txt`, with scoring (`-s`) and profiling (`-p`) enabled.
      * ```bash
        FM_Partition/> python3 p1_partition_eval.py -e YOUR_UT_EID -b BENCHMARK_PATH -s -p
        ```
      * Use help function for more details on how to use this script. `python3 p1_partition_eval.py -h`
      * After running this script, you can find all successfully generated solutions under `output/YOUR_UT_EID/`.
      * If scoring is enabled with `-s`, there will be a `score.csv` under `output/YOUR_UT_EID` to summarize your evaluation results.

# How to Debug
* Write your codes in the `FM_Partition` class.
* You can first use your own evaluation code to debug if you find it more convenient. Create a file `FM_Partition/my_test.py` with the following content. Change `YOUR_UT_EID` to your UT EID.
 ```bash
    import os
    from student_impl.eid_YOUR_UT_EID import FM_Partition
    eid = "YOUR_UT_EID"
    benchmark_path = "benchmarks/example_1.txt"
    output_root = "output"
    output_root = os.path.join(output_root, eid)
    if not os.path.isdir(output_root):
        os.mkdir(output_root)

    output_path = os.path.join(output_root, os.path.basename(benchmark_path))
    solver = FM_Partition()
    solver.read_graph(benchmark_path)
    solution = solver.solve()
    profiling = (0, 0) # ignore runtime and memory for now
    solver.dump_output_file(*solution, *profiling, output_path)
  ```
* Use `pdb` or print function to debug your code.
* Once you successfully dump the solution file `output/YOUR_UT_EID/example_1.txt`, compare it with the ground truth solution `output/reference/example_1.txt`.
* You can also evaluate your code using the evaluation script.
  ```bash
  FM_Partition> python3 p1_partition_eval.py -e YOUR_UT_EID -b ./benchmarks/example_1.txt -s
  ```
* Then, you can further verify your code on other example benchmarks.
* 5 exmaple benchmarks will be provided.

# Tips
* Try to use linear-size data structures like gain buckets, locked nodes, node to net map, net to node map. Try to avoid quadratically-large data structures, e.g., adjacency matrices. The hidden test cases can have a large number of nodes/hyperedges.
* The dumped partition solution should use the original node names in the benchmark file.
* To ensure a **deterministic** solution, please read the **initial solution instruction** in `initialize()`. If multiple solutions have the best cut size, return the **first** best solution.
* Subroutines can be extracted and implemented as methods of the `FM_Partition` class. This can make your `partition_one_pass()` method clean and easy to read.
* Please do not override methods in `FM_Partition_Base`

# Evaluation Metrics
* You will pass a certain test case if
* your code gives the required return values with the required types without exceptions (For python code only)
* your code successfully dumps a valid solution file to `output/YOUR_UT_EID` directory
* and
* your `cut_size_list` exactly matches the ground truth:
  * `tuple(cut_size_list) == tuple(ref_cut_size_list)`
* and
* your bipartition solution is a valid solution that passes the `verify_solution()` (see `verify_solution()` for details):
  * `solver.verify_solution(solution) == True`
* and
* your bipartition solution satisfies the following condition (the order of partition matters, but the order of nodes within each partition does not matter):
  * `set(solution[0]) == set(ref_solution[0]) and set(solution[1]) == set(ref_solution[1])`
* and
* your `min_cut_size` equals the reference value:
  * `min_cut_size == ref_min_cut_size`

# What to Submit if You Use This Python Codebase
Submit the single python script file named `eid_YOUR_UT_EID.py`. Please change `YOUR_UT_EID` to your lowercase UT EID, e.g., `eid_xxxxx.py`.

# How will the TA Evaluate Submitted Python Codes
TA will do the following steps to generate your score summary.
* There are 20 hidden test benchmarks which are randomly generated hypergraphs. Same benchmarks are used for all students. All benchmarks follow the same format as the example benchmarks given to students.
* Copy your file `eid_YOUR_UT_EID.py` to `student_impl/`.
* Run the following command:
  ```bash
  FM_Partition> python3 p1_partition_eval.py -e YOUR_UT_EID -b all -s
  ```
* The generated `score.csv` file under `output/YOUR_UT_EID` will be used in final grading.

# Option to Code in C/C++
You have the option to not use the provided python codebase and implement the FM partition solver in C/C++.
* You need to set up your LRC account if you do not have one and use the LRC's environment for your programming assignment.
* You need to implement everything from scratch, e.g., benchmark parser, solver, dump to solution files, etc.
* You need to submit (change `YOUR_UT_EID` to your lowercase UT EID):
  * A single-file source code named `eid_YOUR_UT_EID.cpp` or `eid_YOUR_UT_EID.c`
  * A shell script (`compile_eid_YOUR_UT_EID.sh`) to compile your C/C++ source code. The generated executable should be named as `exe_eid_YOUR_UT_EID`
* Evaluation
  * TA will copy your `eid_YOUR_UT_EID.cpp` and `compile_eid_YOUR_UT_EID.sh` files to `student_impl/`
  * TA will compile your code as
  ```bash
  FM_Partition> ./student_impl/compile_eid_YOUR_UT_EID.sh
  ```
  * TA will then run your compiled executable as follows,
  ```bash
  FM_Partition> ./student_impl/exe_eid_YOUR_UT_EID ./benchmarks/example_1.txt ./output/YOUR_UT_EID/example_1.txt
  ```
  * TA will run your solver on all hidden test cases, compare your dumped solution files with the ground truth solutions, and use the generated `score.csv` in your final grading.
