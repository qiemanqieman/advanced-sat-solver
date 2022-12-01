import time
import os
import csv

from CDCL import CDCL
from utils import read_cnf, verify


# def parse_args():
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--discount", type=float, metavar="D", default=0.95,
#                         help="discount coefficient for decaying, default 0.95")
#     parser.add_argument("--alpha", type=float, metavar="A", default=0.4,
#                         help="step-size coefficient for algorithms based on ERMA, default 0.4")
#     parser.add_argument("-batch", type=int, metavar="A", default=10,
#                         help="batch parameter used in LRB algorithm, default 10")
#     parser.add_argument("-a", "--assignment-algorithm", type=str, choices=["VSIDS", "ERWA", "RSR", "LRB"],
#                         help="Case-sensitive, heuristic branching algorithm for assigning next literal, default VSIDS",
#                         default=
#                         # "VSIDS"
#                         # "ERWA"
#                         "RSR"
#                         # "LRB"
#                         # "CHB"
#                         )
#     parser.add_argument("-i", "--input", type=str, help="specify the CNF file needed to be solved, default and1.cnf",
#                         default=
#                         # "examples/and1.cnf"
#                         # "examples/and2.cnf"
#                         # "examples/bmc-2.cnf"
#                         # "examples/bmc-7.cnf"
#                         # "my-examples/good-16-vars.cnf"
#                         # "my-examples/bad-12-vars.cnf"
#                         "examples/bmc-1.cnf"
#                         # "my-examples/test.cnf"
#                         # "my-examples/track-main-2018/2d5cc23d8d805a0cf65141e4b4401ba4-20180322_164245263_p_cnf_320_1120.cnf"
#                         # "my-examples/track-main-2018/3c92dedae9bea8c2c22acd655e33d52d-e_rphp065_05.cnf"
#                         )
#     parser.add_argument("-r", "--restart-policy", type=str, choices=["MLR"],
#                         help="specify the restart policy, default to be None, default None", default=
#                         None
#                         # "MLR"
#                         )
#
#     return parser.parse_args()


def testTime():
    # some other parameters:
    Paras = {'discount': 0.95, 'alpha': 0.4, 'batch': 10}

    # all choices for assignment algorithm
    AssignmentAlgorithm = ["VSIDS", "ERWA", "RSR", "LRB", "CHB"]

    # all choices for restart policy
    RestartPolicy = ["MLR", "None"]

    # get all test files
    # assume the test files are all in ./examples
    current_path = os.getcwd()
    file_path = current_path + "\\examples"
    TestFilenames = os.listdir(file_path)

    # save the result in a csv file
    r = open('timeTestResult.csv', 'w', newline="")
    csv_writer = csv.writer(r)
    csv_writer.writerow(["FileName", "AssignmentAlgorithm", "RestartPolicy", "hasSolution", "Time"])

    for testfile in TestFilenames:
        if not testfile.endswith("cnf"):
            continue

        testfile_name = "examples/" + testfile

        for restart_policy in RestartPolicy:
            for assignment_algorithm in AssignmentAlgorithm:
                print(testfile, assignment_algorithm, restart_policy)
                hasSolution = True
                with open(testfile_name, "r") as f:
                    sentence, num_vars = read_cnf(f)

                # Create CDCL solver and solve it!
                if restart_policy == "None":
                    cdcl = CDCL(sentence, num_vars, assignment_algorithm, Paras['alpha'], Paras['discount'],
                                Paras['batch'], None)
                else:
                    cdcl = CDCL(sentence, num_vars, assignment_algorithm, Paras['alpha'], Paras['discount'],
                                Paras['batch'], restart_policy)
                start = time.time()  # compute time
                res = cdcl.solve()
                if res is None:
                    print("NO SOLUTION")
                    hasSolution = False
                end = time.time()
                time_used = end - start
                csv_writer.writerow([testfile, assignment_algorithm, restart_policy, hasSolution, time_used])

    r.close()


if __name__ == "__main__":
    testTime()
