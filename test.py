import time
import os
import csv

from CDCL import CDCL
from tools.utils import read_cnf
from preprocess import init_preprocess_policy

# some other parameters:
Paras = {'discount': 0.95, 'alpha': 0.4, 'batch': 10}

# all choices for assignment algorithm
AssignmentAlgorithm = ["VSIDS", "ERWA", "RSR", "LRB", "CHB"]

# all choices for restart policy
RestartPolicy = ["MLR", "None"]
PreProcessor = ["lighter-NiVER", "None"]
Bandit = ["UCB", "None"]

def testTime():
    # get all test files
    # assume the test files are all in ./examples
    current_path = os.getcwd()
    file_path = current_path + "\\examples"
    TestFilenames = os.listdir(file_path)

    # save the result in a csv file
    r = open('results/timeTestResult.csv', 'w', newline="")
    csv_writer = csv.writer(r)
    csv_writer.writerow(["FileName",
                         "PreProcessor",
                         "RestartPolicy",
                         "Bandit",
                         "AssignmentAlgorithm",
                         "hasSolution",
                         "Time",
                         "PreprocessTime"])

    for testfile in TestFilenames:
        if not testfile.endswith("cnf"):
            continue
        for preprocess_policy in PreProcessor:
            for restart_policy in RestartPolicy:
                for bandit in Bandit:
                    if bandit != "None" and restart_policy == "None":
                        continue
                    if bandit != "None":
                        Res = run_cdcl(testfile, preprocess_policy, restart_policy, bandit, "VSIDS")
                        Res[4] = '/'
                        csv_writer.writerow(Res)
                    else:
                        for assignment_algorithm in AssignmentAlgorithm:
                            Res = run_cdcl(testfile, preprocess_policy, restart_policy, bandit, assignment_algorithm)
                            csv_writer.writerow(Res)

    r.close()


def run_cdcl(testfile, preprocess_policy, restart_policy, bandit, assignment_algorithm):
    print(testfile, preprocess_policy, restart_policy, bandit, assignment_algorithm)
    hasSolution = True
    with open("examples/" + testfile, "r") as f:
        sentence, num_vars = read_cnf(f)

    # Create a preprocessor and preprocess the sentence.
    preprocessor = init_preprocess_policy(preprocess_policy, sentence, num_vars)
    if preprocessor is not None:
        start1 = time.time()
        sentence, removed_clause = preprocessor.preprocess()
        end1 = time.time()
        if removed_clause is None:
            print("✘ No solution found")
            hasSolution = False
            Res = [testfile, preprocess_policy, restart_policy, bandit, assignment_algorithm, hasSolution, '/',
                 end1 - start1]
            return Res

    # Create CDCL solver and solve it!
    if restart_policy == "None":
        restart_policy = None

    if bandit == "None":
        bandit = None

    cdcl = CDCL(sentence, num_vars,
                assignment_algorithm,
                Paras['alpha'],
                Paras['discount'],
                Paras['batch'],
                restart_policy,
                bandit)

    start = time.time()  # compute time
    res = cdcl.solve()
    end = time.time()
    time_used = end - start

    if res is None:
        print("NO SOLUTION")
        hasSolution = False

    if preprocessor is None:
        preprocess_time = None
    else:
        preprocess_time = end1 - start1

    Res = [testfile, preprocess_policy, restart_policy, bandit, assignment_algorithm, hasSolution, time_used, preprocess_time]
    return Res


if __name__ == "__main__":
    testTime()
