#########################################
# Evaluate your implementation
# Please do not change codes in this file
#########################################
import importlib
import os
import traceback

import numpy as np
import argparse


def evaluate(
    eid: str,
    benchmark_root: str,
    output_root: str,
    impl_package: str,
    module_name: str,
    profile: bool,
    *args,
    **kwargs,
):
    """Evaluate one or all benchmarks for one student. The solver will partitions of the hypergraph and dump the solution files.

    Args:
        eid (str): your UT EID
        benchmark_root (str): path to the benchmark dir
        output_root (str): path to the output root dir
        impl_package (str): package name of the student implementation
        module_name (str): class name of the partition solver
        profile (bool): whether to profile runtime and memory
    """
    eid = eid.lower()
    output_root = os.path.join(output_root, eid)
    if not os.path.isdir(output_root):
        os.mkdir(output_root)
    if os.path.isdir(benchmark_root):
        benchmarks = [os.path.join(benchmark_root, i) for i in os.listdir(benchmark_root)]
    elif os.path.isfile(benchmark_root):
        benchmarks = [benchmark_root]
    else:
        raise ValueError(f"Benchmark dir or path not found: {benchmark_root}")
    module = importlib.import_module(f".eid_{eid}", f"{impl_package}")

    solver = getattr(module, module_name)(*args, **kwargs)
    failed = 0
    for benchmark in benchmarks:
        solver.read_graph(benchmark)
        try:
            solution = solver.solve()
            if profile:
                profiling = solver.profile(n_runs=10)
            else:
                profiling = 0, 0
            output_path = os.path.join(output_root, os.path.basename(benchmark))
            solver.dump_output_file(*(solution + profiling), output_path)
        except Exception as e:
            traceback.print_exc()
            print(f"Fail to generate output on benchmark: {benchmark}")
            failed += 1
    print(
        f"Finish evaluation for student EID: {eid:10s} Success: {len(benchmarks)-failed} / {len(benchmarks)}"
    )


def score(
    eid: str,
    benchmark_root: str,
    ref_output_root: str,
    output_root: str,
    impl_package: str,
    module_name: str,
    *args,
    **kwargs,
):
    """This function will compare the dumped solution files with the ground truth solutions and generate score.csv file as the score summary

    Args:
        eid (str): your UT EID
        benchmark_root (str): path to the benchmark dir
        ref_output_root (str): path to the reference output dir
        output_root (str): path to the output root dir
        impl_package (str): package name of the student implementation
        module_name (str): class name of the partition solver
    """
    eid = eid.lower()
    output_root = os.path.join(output_root, eid)

    if os.path.isdir(benchmark_root):
        benchmarks = [os.path.join(benchmark_root, i) for i in os.listdir(benchmark_root)]
    elif os.path.isfile(benchmark_root):
        benchmarks = [benchmark_root]
    else:
        raise ValueError(f"Benchmark dir or path not found: {benchmark_root}")

    module = importlib.import_module(f".eid_{eid}", f"{impl_package}")

    solver = getattr(module, module_name)(*args, **kwargs)
    success_list = [["benchmark", "passed", "note", "runtime", "memory"]]
    for benchmark in benchmarks:
        benchmark_name = os.path.basename(benchmark)
        solver.read_graph(benchmark)
        output_path = os.path.join(output_root, benchmark_name)
        if not os.path.exists(output_path):
            print(f"Fail to load student {eid} solution {benchmark_name}")
            success = [benchmark_name, False, "SOLUTION_NOT_FOUND", 0, 0]
        else:
            try:
                ref_output_path = os.path.join(ref_output_root, benchmark_name)
                cut_size_list, solution, min_cut_size, runtime, used_mem = solver.load_solution(output_path)
                (
                    ref_cut_size_list,
                    ref_solution,
                    ref_min_cut_size,
                    ref_runtime,
                    ref_used_mem,
                ) = solver.load_solution(ref_output_path)

                if tuple(cut_size_list) != tuple(ref_cut_size_list):
                    success = [benchmark_name, False, "CUT_SIZE_LIST_MISMATCH", runtime, used_mem]
                else:
                    if not solver.verify_solution(solution):
                        success = [benchmark_name, False, "INVALID_SOLUTION", runtime, used_mem]
                    else:
                        if set(solution[0]) != set(ref_solution[0]) or set(solution[1]) != set(ref_solution[1]):
                            success = [benchmark_name, False, "PARTITION_MISMATCH", runtime, used_mem]
                        else:
                            if min_cut_size != ref_min_cut_size:
                                success = [benchmark_name, False, "MIN_CUT_SIZE_MISMATCH", runtime, used_mem]
                            else:
                                success = [benchmark_name, True, "PASSED", runtime, used_mem]
            except Exception as e:
                print(f"Fail to score student {eid} solution {benchmark_name}")
                traceback.print_exc()
                success = [benchmark_name, False, "SOLUTION_LOAD_ERROR", 0, 0]
        success_list.append(success)
    passed = sum(i[1] for i in success_list[1:])
    success_list.append(["passed/total", str(passed), str(len(benchmarks)), "-", "-"])
    success_list = np.array(success_list)
    print(f"Finish grading for student EID: {eid:10s} Grade: {passed} / {len(benchmarks)}")
    np.savetxt(os.path.join(output_root, "score.csv"), success_list, fmt="%s", delimiter=",")
    return passed, len(benchmarks)


benchmark_root = "benchmarks"
output_root = "output"
ref_output_root = "output/reference"
impl_package = "student_impl"
module_name = "FM_Partition"


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("-e", "--eid", required=True, type=str, help="Your lowercase UT EID, e.g., -e xxxxx")
    parser.add_argument(
        "-b",
        "--benchmark",
        required=False,
        default="all",
        type=str,
        help="One benchmark path or 'all' indicates all benchmarks, e.g., -b ./benchmarks/example_1.txt or -b all. Defaults to 'all'.",
    )
    parser.add_argument(
        "-p",
        "--profile",
        required=False,
        action="store_true",
        default=False,
        help="Whether to perform runtime and memory profiling (Might be slow). Defaults to False. To enable it, add '-p' to your argument",
    )
    parser.add_argument(
        "-s",
        "--score",
        required=False,
        action="store_true",
        help="Whether to compare with reference solutions and generate scores. Defaults to False. To enable it, add '-s' to your argument",
    )

    args = parser.parse_args()
    evaluate(
        args.eid,
        benchmark_root if args.benchmark.lower() == "all" else args.benchmark,
        output_root,
        impl_package,
        module_name,
        profile=args.profile,
    )
    if args.score:
        score(
            args.eid,
            benchmark_root if args.benchmark.lower() == "all" else args.benchmark,
            ref_output_root,
            output_root,
            impl_package,
            module_name,
        )
