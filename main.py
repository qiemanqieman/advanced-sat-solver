import argparse
import time

from cdcl import cdcl
from utils import read_cnf, verify


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--assignment_alogrithm", type=str, default="LRB")
    parser.add_argument(
        # "-i", "--input", type=str, default="examples/and1.cnf"
        # "-i", "--input", type=str, default="examples/and2.cnf"
        # "-i", "--input", type=str, default="examples/bmc-1.cnf"
        # "-i", "--input", type=str, default="examples/bmc-2.cnf",
        "-i", "--input", type=str, default="examples/bmc-7.cnf"
        # "-i", "--input", type=str, default="my-examples/track-main-2018/2d5cc23d8d805a0cf65141e4b4401ba4-20180322_164245263_p_cnf_320_1120.cnf"
        # "-i", "--input", type=str, default="my-examples/good-16-vars.cnf"
        # "-i", "--input", type=str, default="my-examples/bad-12-vars.cnf"
        # "-i", "--input", type=str, default="my-examples/test.cnf"
    )

    return parser.parse_args()


def main(args):
    # Create problem.
    with open(args.input, "r") as f:
        sentence, num_vars = read_cnf(f)

    # NOTE compute time
    start = time.time()
    # Create CDCL solver and solve it!
    res = cdcl(sentence, num_vars, args.assignment_alogrithm)

    if res is None:
        print("✘ No solution found")
    else:
        print(f"✔ Successfully found a solution: {res}")
    end = time.time()
    print(end - start, "seconds elapsed")
    if res is not None:
        print("The solution is verified to be", verify(sentence, res))


if __name__ == "__main__":
    args = parse_args()
    main(args)
