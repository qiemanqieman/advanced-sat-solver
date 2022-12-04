def read_cnf(fp):
    sentence = []
    for line in fp:
        if line.startswith('c'):
            continue
        if line.startswith('p'):
            line = line.split()
            num_vars, num_clauses = int(line[2]), int(line[3])
        else:
            line = line.split()
            clause = [int(x) for x in line[:-1]]
            sentence.append(clause)
    assert len(sentence) == num_clauses
    return sentence, num_vars


def verify(sentence, solution):
    """
    verify whether a solution for SAT is right or not
    :param sentence: list[list] of int, list of clause
    :param solution: list of int, signed literals, -5 means variable_5 is False(or in other word, literal_-5 is True)
    :return: True or False
    """
    solution = set(solution)

    def clause_is_true(cl):
        return any([literal in solution for literal in cl])

    return all([clause_is_true(clause) for clause in sentence])


def check(res, num_vars, sentence):
    # assert len(res) == num_vars
    import numpy as np
    abs_res = [abs(literal) for literal in res]
    cnt = np.zeros(num_vars+1)
    cnt[0] = 1
    for var in abs_res:
        cnt[var] += 1
    for i in range(len(cnt)):
        if cnt[i] > 1:
            print("wrong", i, cnt[i])
            return False
    for clause in sentence:
        if not any(literal in res for literal in clause):
            print("error", clause)
            return False
    print("pass check!")
    return True
