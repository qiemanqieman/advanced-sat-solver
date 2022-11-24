import time
import argparse

from CDCL import CDCL
from utils import read_cnf, verify


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--discount", type=float, metavar="D", default=0.95, help="discount coefficient for decaying")
    parser.add_argument("--alpha", type=float, metavar="A", default=0.4, help="step-size coefficient for algorithms based on ERMA")
    parser.add_argument("-batch", type=int, metavar="A", default=10, help="batch parameter used in LRB algorithm")
    parser.add_argument("-a", "--assignment-alogrithm", type=str, choices=["VSIDS", "ERWA", "RSR", "LRB"],
                        help="Case-sensitive, heuristic branching algorithm for assigning next literal",
                        default=
                        # "VSIDS"
                        # "ERWA"
                        "RSR"
                        # "LRB"
                        )
    parser.add_argument("-i", "--input", type=str, help="specify the CNF file needed to be solved", default=
                        # "examples/and1.cnf"
                        # "examples/and2.cnf"
                        "examples/bmc-1.cnf"
                        # "examples/bmc-2.cnf"
                        # "examples/bmc-7.cnf"
                        # "my-examples/track-main-2018/2d5cc23d8d805a0cf65141e4b4401ba4-20180322_164245263_p_cnf_320_1120.cnf"
                        # "my-examples/track-main-2018/3c92dedae9bea8c2c22acd655e33d52d-e_rphp065_05.cnf"
                        # "my-examples/good-16-vars.cnf"
                        # "my-examples/bad-12-vars.cnf"
                        # "my-examples/test.cnf"
                        )

    return parser.parse_args()


def main(args):
    # Create problem.
    with open(args.input, "r") as f:
        sentence, num_vars = read_cnf(f)

    # Create CDCL solver and solve it!
    cdcl = CDCL(sentence, num_vars, args.assignment_alogrithm, args.alpha, args.discount, args.batch)
    start = time.time()  # compute time
    res = cdcl.solve()
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
