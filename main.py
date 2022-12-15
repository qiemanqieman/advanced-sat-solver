import time
import argparse

from CDCL import CDCL
from utils import read_cnf, verify
from preprocess import init_preprocess_policy, after_assignment


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--discount", type=float, metavar="D", default=0.95,
                        help="discount coefficient for decaying, default 0.95")
    parser.add_argument("--alpha", type=float, metavar="A", default=0.4,
                        help="step-size coefficient for algorithms based on ERMA, default 0.4")
    parser.add_argument("-batch", type=int, metavar="A", default=10,
                        help="batch parameter used in LRB algorithm, default 10")
    parser.add_argument("-a", "--assignment-algorithm", type=str, choices=["VSIDS", "ERWA", "RSR", "LRB", "UCB"],
                        help="Case-sensitive, heuristic branching algorithm for assigning next literal, default VSIDS",
                        default=
                        "ERWA"
                        # "ERWA"
                        # "RSR"
                        # "LRB"
                        # "CHB"
                        )
    parser.add_argument("-i", "--input", type=str, help="specify the CNF file needed to be solved, default and1.cnf",
                        default=
                        # "examples/and1.cnf"
                        # "examples/and2.cnf"
                        # "examples/bmc-2.cnf"
                        # "examples/bmc-7.cnf"
                        # "my-examples/good-16-vars.cnf"
                        # "my-examples/bad-12-vars.cnf"
                        "examples/bmc-1.cnf"
                        # "my-examples/test.cnf"
                        # "my-examples/track-main-2018/2d5cc23d8d805a0cf65141e4b4401ba4-20180322_164245263_p_cnf_320_1120.cnf"
                        # "my-examples/track-main-2018/3c92dedae9bea8c2c22acd655e33d52d-e_rphp065_05.cnf"
                        )
    parser.add_argument("-r", "--restart-policy", type=str, choices=["MLR"],
                        help="specify the restart policy, default to be None, default None", default=
                        # None
                        "MLR"
                        )
    parser.add_argument("-p", "--preprocess-policy", type=str, choices=["NiVER", "lighter-NiVER"],
                        help="specify the preprocess policy, default to be None, default None", default=
                        None
                        # "NiVER"
                        # "lighter-NiVER"
                        )
    parser.add_argument("-b", "--bandit", type=str, choices=["UCB"],
                        help="specify the heuristic changing policy", default=
                        "UCB"
                        )

    return parser.parse_args()


def main(args):
    # Create problem.
    with open(args.input, "r") as f:
        sentence, num_vars = read_cnf(f)
    origin_sentence = list(sentence)

    # Create a preprocessor and preprocess the sentence.
    preprocessor = init_preprocess_policy(args.preprocess_policy, sentence, num_vars)
    if preprocessor is not None:
        start1 = time.time()
        sentence, removed_clause = preprocessor.preprocess()
        end1 = time.time()
        if removed_clause is None:
            print("✘ No solution found")
            return

    # Create CDCL solver and solve it!
    cdcl = CDCL(sentence, num_vars, args.assignment_algorithm, args.alpha, args.discount, args.batch,
                args.restart_policy, args.bandit)
    start = time.time()  # compute time
    res = cdcl.solve()
    end = time.time()
    if res is None:
        print("✘ No solution found")
    else:
        if preprocessor is not None:
            res = after_assignment(num_vars, removed_clause, res)
        print(f"✔ Successfully found a solution: {res}")
    if preprocessor is not None:
        print(end1 - start1, "seconds for preprocess")
    print(end - start, "seconds elapsed")
    if res is not None:
        print("The solution is verified to be", verify(origin_sentence, res))

if __name__ == "__main__":
    args = parse_args()
    main(args)
