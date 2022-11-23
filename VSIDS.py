import bisect


def init_vsids_scores(sentence, num_vars):
    """Initialize variable scores for VSIDS.
    we need to design it to be in order(in my case, decreasing order), so that accelerate deciding"""
    scores = {}
    """ YOUR CODE HERE """
    # from queue import PriorityQueue as PQ
    # scores = PQ()
    # for clause in sentence:
    #     for literal in clause:
    #         scores.put((-len(clause), literal))
    for clause in sentence:
        for literal in clause:
            scores[literal] = scores.get(literal, 0) + 1
    return dict(sorted(scores.items(), key=lambda i: i[1], reverse=True))


def decide_vsids(vsids_scores, assignment):
    """Decide which variable to assign and whether to assign True or False.
    reset value to 0 for those have been assigned and reposition to the end so that new learned clause's literal will have
    more chance to be chosen"""
    assigned_lit = None

    """ YOUR CODE HERE """
    scores = dict(vsids_scores)
    reset = []
    for lit in scores:
        if lit in assignment[0] or -lit in assignment[0]:
            vsids_scores.pop(lit)
            reset.append((lit, 0))
            continue
        assigned_lit = lit
        break
    vs = dict(list(vsids_scores.items()) + reset)
    vsids_scores.clear()
    vsids_scores.update(vs)
    return assigned_lit


def update_vsids_scores(vsids_scores, learned_clause, decay=0.95):
    """Update VSIDS scores.
    note that the sorting order should be maintained"""
    increased = []
    for lit in learned_clause:
        increased.append([(vsids_scores.pop(lit) + 1) * decay, lit])
    for lit in vsids_scores:
        vsids_scores[lit] = vsids_scores[lit] * decay
    scores = [[i[1], i[0]] for i in vsids_scores.items()]
    scores.reverse()
    for i in increased:
        bisect.insort(scores, i)  # use bisect method for accelerating the operation of maintaining order
    scores.reverse()
    scores = [(i[1], i[0]) for i in scores]
    scores = dict(scores)
    vsids_scores.clear()
    vsids_scores.update(scores)
