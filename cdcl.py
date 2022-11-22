import bisect


def bcp(sentence, assignment, c2l_watch, l2c_watch, is_backtrack=False):
    """Propagate unit clauses with watched literals."""

    """ YOUR CODE HERE """
    def propagate_watch(idx, clause_idx):
        is_unit_or_conflict = True
        for literal in sentence[clause_idx]:  # o.s. checking for all literal in clause
            # if having satisfied literal, check next clause
            if literal in assignment[0]:
                is_unit_or_conflict = False
                idx += 1
                break
            # if having any literal whose negation unassigned, adjust watching literals for this clause, o.w.
            # this clause is unit or conflict
            if literal not in c2l_watch[clause_idx] and -literal not in assignment[0]:
                c2l_watch[clause_idx].remove(-assignment[0][i])
                l2c_watch[-assignment[0][i]].remove(clause_idx)
                c2l_watch[clause_idx].append(literal)
                l2c_watch[literal] = l2c_watch.get(literal, []) + [clause_idx]
                is_unit_or_conflict = False
                break
        return idx, is_unit_or_conflict

    def check_satisfied(i0, i1, literal_idx):
        """check if clause already sat or has two validate literals watching"""
        satisfied = False
        if any([i0 in assignment[0], i1 in assignment[0]]) or all([-i0 not in assignment[0], -i1 not in assignment[0]]):
            literal_idx += 1
            satisfied = True
        return satisfied, literal_idx

    def check_if_backtrack():
        """check if the bcp is rerun after a conflict backtracking"""
        if is_backtrack:  # if rerun bcp after backtracking, assign value for the newly learned unit clause
            assignment[0].append(c2l_watch[len(sentence) - 1][0])
            assignment[1].append(len(sentence) - 1)
            return 1
        return 0

    def handle_first_time_to_run():
        """handle run bcp for the first time, handle all clauses with only 1 literal"""
        conflict_clause = None
        for clause_idx, literals in c2l_watch.items():
            if len(literals) == 1:  # unit clause
                if -literals[0] in assignment:
                    conflict_clause = list(sentence[clause_idx])
                    break
                if literals[0] not in assignment:
                    assignment[0].append(literals[0])
                    assignment[1].append(clause_idx)
        return conflict_clause

    i = len(assignment[0]) - 1
    i += check_if_backtrack()
    if not assignment[0]:  # first time to run bcp
        i = 0
        conflict_clause = handle_first_time_to_run()
        if conflict_clause: return conflict_clause
    while i < len(assignment[0]):  # iterate all new assignments
        literal_idx, watch_clauses = 0, l2c_watch.get(-assignment[0][i], [])
        while literal_idx < len(watch_clauses):  # iterate all clause
            clause_idx = watch_clauses[literal_idx]
            i0, i1 = c2l_watch[clause_idx]
            satisfied, literal_idx = check_satisfied(i0, i1, literal_idx)
            if satisfied: continue
            literal_idx, is_unit_or_conflict = propagate_watch(literal_idx, clause_idx)
            if is_unit_or_conflict:
                literal_idx += 1
                another = i0 if i0 != -assignment[0][i] else i1
                if -another in assignment[0]:  # conflicted clause
                    return list(sentence[clause_idx])
                assignment[0].append(another)   # unit clause
                assignment[1].append(clause_idx)
        i += 1
    return None  # indicate no conflict; other return the antecedent of the conflict


def init_vsids_scores(sentence, num_vars):
    """Initialize variable scores for VSIDS.
    we need to design it to be in order(in my case, decreasing order), so that accelerate deciding"""
    scores = {}

    """ YOUR CODE HERE """
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
    scores = {}
    scores.update(vsids_scores)
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
    scores = [[i[1], i[0]] for i in scores]
    scores = dict(scores)
    vsids_scores.clear()
    vsids_scores.update(scores)


def init_watch(sentence, num_vars):
    """Initialize the watched literal data structure."""
    c2l_watch = {}  # clause -> literal
    l2c_watch = {}  # literal -> watch

    """ YOUR CODE HERE """
    for i in range(len(sentence)):
        c2l_watch[i] = [sentence[i][0]]
        l2c_watch[sentence[i][0]] = l2c_watch.get(sentence[i][0], []) + [i]
        if len(sentence[i]) > 1:
            c2l_watch[i].append(sentence[i][1])
            l2c_watch[sentence[i][1]] = l2c_watch.get(sentence[i][1], []) + [i]
    return c2l_watch, l2c_watch


def analyze_conflict(sentence, assignment, decided_idxs, conflict_ante):
    """Analyze the conflict with first-UIP clause learning.
    resolve conflict clause with its last assigned literal's ante-clause until only one literal having the highest
    level in conflict clause
    learned clause returned should be in decreasing order of the assignment, which means the latest assigned literal
    is in the start. This will facilitate the later call of add_learned_clause(...)"""
    backtrack_level, learned_clause = None, []

    """ YOUR CODE HERE """

    def resolve(clause1, clause2):
        """resolve two clause, one is conflict clause, another is unit clause, the result is conflict clause"""
        c = set(clause1 + clause2)
        clause = [l for l in c if -l not in c]
        return clause

    def level_of(literal):
        """compute level of assigned literal"""
        index = assignment[0].index(literal)
        for i in range(len(decided_idxs)):
            if index < decided_idxs[i]:
                return i
        return len(decided_idxs)

    def conflict_clause_level_is_0(clause):
        """compute the level of a conflict clause --- the highest level of all literals' negations in clause"""
        return all([level_of(-literal) == 0 for literal in clause])

    if conflict_clause_level_is_0(conflict_ante):
        return -1, learned_clause

    # get the highest level's assignments
    assignments = [list(assignment[0][decided_idxs[-1]:]), list(assignment[1][decided_idxs[-1]:])]
    assignments[0].reverse()  # and put the latest assigned to the start
    assignments[1].reverse()
    highest_level_literals = [-literal for literal in assignments[0] if -literal in conflict_ante]
    while len(highest_level_literals) > 1:
        conflict_ante = resolve(conflict_ante, sentence[assignment[1][assignment[0].index(-highest_level_literals[0])]])
        highest_level_literals = [-literal for literal in assignments[0] if -literal in conflict_ante]
    if len(highest_level_literals) == 1:
        learned_clause = sorted(conflict_ante, key=lambda key: level_of(-key), reverse=True)
        backtrack_level = 0 if len(learned_clause) == 1 else level_of(-learned_clause[1])
    return backtrack_level, learned_clause


def backtrack(assignment, decided_idxs, level):
    """Backtrack by deleting assigned variables.
    keep all assigned literals with level <= backtrack_level"""

    """ YOUR CODE HERE """
    new_ass = [assignment[0][:decided_idxs[level]], assignment[1][:decided_idxs[level]]]
    new_dec = decided_idxs[:level]
    assignment.clear()
    assignment += new_ass
    decided_idxs.clear()
    decided_idxs += new_dec


def add_learned_clause(sentence, learned_clause, c2l_watch, l2c_watch):
    """Add learned clause to the sentence and update watch.
    learned_clause is unit and in decreasing order of assignment. We choose to watch the first literal which
    is the only one satisfiable. This can promise least check of this clause for later rerun `bcp(...)` """

    """ YOUR CODE HERE """
    i = len(sentence)
    sentence.append(learned_clause)
    c2l_watch[i] = [sentence[i][0]]
    l2c_watch.update({sentence[i][0]: l2c_watch.get(sentence[i][0], []) + [i]})
    if len(sentence[i]) > 1:
        c2l_watch[i].append(sentence[i][1])
        l2c_watch.update({sentence[i][1]: l2c_watch.get(sentence[i][1], []) + [i]})


def cdcl(sentence, num_vars):
    """Run a CDCL solver for the SAT problem.

    To simplify the use of data structures, `sentence` is a list of lists where each list
    is a clause. Each clause is a list of literals, where a literal is a signed integer.
    `assignment` is also a list of literals in the order of their assignment.
    """
    # Initialize some data structures.
    vsids_scores = init_vsids_scores(sentence, num_vars)
    c2l_watch, l2c_watch = init_watch(sentence, num_vars)
    assignment, decided_idxs = [[], []], []

    # Run BCP.
    if bcp(sentence, assignment, c2l_watch, l2c_watch) is not None:
        return None  # indicate UNSAT

    # Main loop.
    while len(assignment[0]) < num_vars:
        assigned_lit = decide_vsids(vsids_scores, assignment)
        # NOTE
        if assigned_lit is None:  # all variables are assigned(find an assignment), finish the loop
            return assignment[0]
        decided_idxs.append(len(assignment[0]))
        assignment[0].append(assigned_lit)
        assignment[1].append(None)

        # Run BCP.
        conflict_ante = bcp(sentence, assignment, c2l_watch, l2c_watch)
        while conflict_ante is not None:
            # Learn conflict.
            backtrack_level, learned_clause = analyze_conflict(sentence, assignment, decided_idxs, conflict_ante)
            if backtrack_level < 0:  # conflict clause level is 0, UNSAT, finish the loop
                return None
            add_learned_clause(sentence, learned_clause, c2l_watch, l2c_watch)
            # Update VSIDS scores.

            update_vsids_scores(vsids_scores, learned_clause)

            # Backtrack.

            backtrack(assignment, decided_idxs, backtrack_level)

            # Propagate watch.
            conflict_ante = bcp(sentence, assignment, c2l_watch, l2c_watch, True)

    return assignment[0]  # indicate SAT
