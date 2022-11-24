from heuristics import LRB, VSIDS
from AssignInfo import AssignInfo


class CDCL:
    def __init__(self, sentence, num_vars, assignment_algorithm):
        """To simplify the use of data structures, `sentence` is a list of lists where each list
        is a clause. Each clause is a list of literals, where a literal is a signed integer.
        `assignment` is also a list of literals in the order of their assignment.
        """
        # Initialize some data structures.
        self.sentence = sentence
        self.num_vars = num_vars
        self.c2l_watch, self.l2c_watch = self._init_watch()
        self.ai = AssignInfo()
        if assignment_algorithm.lower() == 'lrb':
            self.heuristic = LRB(sentence, 0.4)
        elif assignment_algorithm.lower() == 'vsids':
            self.heuristic = VSIDS(sentence, 0.95)

    def solve(self):
        """Run the `CDCL` solver for the `SAT` problem.
        This is the only interface for users.
        """
        # Run BCP.
        if self._bcp(): return None  # indicate UNSAT

        # Main loop.
        while len(self.ai.assigned) < self.num_vars:
            assigned_lit = self.heuristic.decide(self.ai.assigned)
            # NOTE
            if assigned_lit is None:  # all variables are assigned(find an assignment), finish the loop
                return self.ai.assignment
            self.ai.decided_idxs.append(len(self.ai.assigned))
            self._handle_assign(assigned_lit, None)
            # Run BCP.
            conflict_ante = self._bcp()
            while conflict_ante:
                # Learn conflict.
                backtrack_level, learned_clause, conflict_side_literals = self._analyze_conflict(conflict_ante)
                if backtrack_level < 0:  # conflict clause level is 0, UNSAT, finish the loop
                    return None
                self._add_learned_clause(learned_clause)
                self.heuristic.after_conflict_analysis(learned_clause, conflict_side_literals)

                # Backtrack.
                self._backtrack(backtrack_level)

                # Propagate watch.
                conflict_ante = self._bcp(True)

        return self.ai.assignment  # indicate SAT

    def _handle_assign(self, lit, ante):
        """Assign a literal. maintain relevant data structure"""
        self.ai.on_assign(lit, ante)
        self.heuristic.on_assign(lit)

    def _init_watch(self):
        """Initialize the watched literal data structure."""
        c2l_watch, l2c_watch = {}, {}  # c2l_watch: clause to literal watch, l2c_watch: literal to clause watch
        for i in range(len(self.sentence)):
            c2l_watch[i] = [self.sentence[i][0]]
            l2c_watch[self.sentence[i][0]] = l2c_watch.get(self.sentence[i][0], []) + [i]
            if len(self.sentence[i]) > 1:
                c2l_watch[i].append(self.sentence[i][1])
                l2c_watch[self.sentence[i][1]] = l2c_watch.get(self.sentence[i][1], []) + [i]
        return c2l_watch, l2c_watch

    def _bcp(self, is_backtrack=False):
        """Boolean constraint propagation with 2 watched literals per clause."""
        i = len(self.ai.assigned) - 1
        if is_backtrack:
            i += 1
            self._handle_backtrack()
        if not self.ai.assigned:  # first time to run bcp
            i = 0
            conflict_clause = self._handle_first_time_to_run()
            if conflict_clause: return conflict_clause
        while i < len(self.ai.assigned):  # iterate all new assignments
            handle_lit = -self.ai.assignment[i]
            watch_clauses, idx = self.l2c_watch.get(handle_lit, []), 0
            while idx < len(watch_clauses):  # iterate all clause
                clause_idx = watch_clauses[idx]
                l0, l1 = self.c2l_watch[clause_idx]
                satisfied = self._check_satisfied(l0, l1)
                if satisfied:
                    idx += 1
                    continue
                propagated, is_unit_or_conflict = self._propagate_watch_on_clause(handle_lit, clause_idx)
                if not propagated: idx += 1
                if is_unit_or_conflict:
                    conflict_clause = self._handle_unit_or_conflict(clause_idx, l0, l1, handle_lit)
                    if conflict_clause: return conflict_clause
            i += 1
        return None  # indicate no conflict; other return the antecedent of the conflict

    def _propagate_watch_on_clause(self, lit, clause_idx):
        """propagate watching literal on a clause(sentence[clause_idx]).
        try to find a new literal to replace currently watching literal(lit)"""
        propagated, is_unit_or_conflict = False, True
        for literal in self.sentence[clause_idx]:  # o.s. checking for all literal in clause
            # if having satisfied literal, check next clause
            if literal in self.ai.assigned:
                is_unit_or_conflict = False
                break
            # if having any literal whose negation unassigned, adjust watching literals for this clause,
            # o.w., this clause is unit or conflict
            if literal not in self.c2l_watch[clause_idx] and -literal not in self.ai.assigned:
                self.c2l_watch[clause_idx].remove(lit)
                self.l2c_watch[lit].remove(clause_idx)
                self.c2l_watch[clause_idx].append(literal)
                self.l2c_watch[literal] = self.l2c_watch.get(literal, []) + [clause_idx]
                is_unit_or_conflict = False
                propagated = True
                break
        return propagated, is_unit_or_conflict

    def _check_satisfied(self, l0, l1):
        """check if clause already sat or already has two validate literals watching"""
        satisfied = False
        if any([l0 in self.ai.assigned, l1 in self.ai.assigned]) or all(
                [-l0 not in self.ai.assigned, -l1 not in self.ai.assigned]):
            satisfied = True
        return satisfied

    def _handle_backtrack(self):
        """when the bcp is rerun after a conflict backtracking, add the newly learned unit clause's literal
        to the assignment
        """
        self._handle_assign(self.c2l_watch[len(self.sentence) - 1][0], len(self.sentence) - 1)

    def _handle_first_time_to_run(self):
        """handle run bcp for the first time, handle all clauses with only 1 literal"""
        for clause_idx, literals in self.c2l_watch.items():
            if len(literals) == 1:  # unit clause
                if -literals[0] in self.ai.assigned:
                    return list(self.sentence[clause_idx])
                if literals[0] not in self.ai.assigned:
                    self._handle_assign(literals[0], clause_idx)
        return None

    def _handle_unit_or_conflict(self, clause_idx, l0, l1, handle_lit):
        """handle unit clause or conflict clause"""
        another = l0 if l0 != handle_lit else l1
        if -another in self.ai.assigned:  # conflicted clause
            return list(self.sentence[clause_idx])
        self._handle_assign(another, clause_idx)
        return None

    def _analyze_conflict(self, conflict_ante):
        """
        Analyze the conflict with first-UIP clause learning.
        resolve conflict clause with its last assigned literal's ante-clause until only one literal having the highest
        level in conflict clause
        learned clause returned should be in decreasing order of the assignment, which means the latest assigned literal
        is in the start. This will facilitate the later call of add_learned_clause(...)"""
        return self.ai.analyse_conflict(self.sentence, conflict_ante)

    def _backtrack(self, level):
        """Backtrack by deleting assigned variables.
        keep all assigned literals with level <= backtrack_level"""
        unassigned_lits = self.ai.backtrack(level)
        for lit in unassigned_lits:
            self.heuristic.on_unassign(lit)
        self.heuristic.rearrange(unassigned_lits)

    def _add_learned_clause(self, learned_clause):
        """Add learned clause to the sentence and update watch.
        learned_clause is unit and in decreasing order of assignment. We choose to watch the first literal which
        is the only one satisfiable. This can promise least check of this clause for later rerun `bcp(...)` """
        i = len(self.sentence)
        self.sentence.append(learned_clause)
        self.c2l_watch[i] = [self.sentence[i][0]]
        self.l2c_watch.update({self.sentence[i][0]: self.l2c_watch.get(self.sentence[i][0], []) + [i]})
        if len(self.sentence[i]) > 1:
            self.c2l_watch[i].append(self.sentence[i][1])
            self.l2c_watch.update({self.sentence[i][1]: self.l2c_watch.get(self.sentence[i][1], []) + [i]})
