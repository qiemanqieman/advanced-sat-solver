class NiVER:
    """Preprocess based on Non Increasing VER (NiVER)"""

    def __init__(self, sentence, num_vars, flag):

        self.sentence = sentence
        self.num_vars = num_vars
        self.l2c_all, self.num_lit = self._init_watch()
        self.removed_clause = []    # clauses removed during preprocessing
        self.flag = flag    # degree of preprocess

    def preprocess(self):
        """The main part for preprocess with NiVER algorithm."""
        while True:
            entry = False
            for var in range(1, self.num_vars + 1):
                if len(self.l2c_all[var]) == 0 or len(self.l2c_all[-var]) == 0:
                    continue
                R_clause_set = []
                new_num_lit = 0
                old_num_lit = self.num_lit[var] + self.num_lit[-var]
                for P in self.l2c_all[var]:
                    for N in self.l2c_all[-var]:
                        resolvent = self.learn_resolvent(list(P), list(N), var)
                        if len(resolvent) == 0:
                            return None, None
                        if not self.judge_tautology(resolvent) and not self.judge_exist(resolvent):
                            new_num_lit += len(resolvent)
                            R_clause_set.append(resolvent)
                            if new_num_lit > old_num_lit:
                                break
                    if new_num_lit > old_num_lit:
                        break

                if old_num_lit >= new_num_lit:
                    self.removed_clause.append((var, self.l2c_all[var] + self.l2c_all[-var]))
                    self.remove_c(var)
                    self.remove_c(-var)
                    for clause in R_clause_set:
                        self.sentence.append(clause)
                        for lit in clause:
                            self.l2c_all[lit].append(clause)
                            self.num_lit[lit] += len(clause)
                    if self.flag:
                        entry = True
            if not entry:
                break
        return self.sentence, self.removed_clause

    def _init_watch(self):
        """Initialize the l2c_all and num_lit."""
        l2c_all = {}    # literal -> clause
        num_lit = []    # literal -> number of literals
        for i in range(-self.num_vars, self.num_vars + 1):
            l2c_all[i] = []
            num_lit.append(0)
        for idx, clause in enumerate(self.sentence):
            for lit in clause:
                l2c_all[lit].append(clause)
                num_lit[lit] += len(clause)
        return l2c_all, num_lit

    def learn_resolvent(self, P_clause, N_clause, var):
        """Eliminate the Variable numbered var, and return the resolvent."""
        P_clause.remove(var)
        N_clause.remove(-var)
        resolvent = list(set(P_clause + N_clause))
        return resolvent

    def judge_tautology(self, clause):
        """Determine whether a clause is a tautology."""
        for lit in clause:
            if -lit in clause:
                return True
        return False

    def judge_exist(self, clause):
        """Determine whether a clause has already existed in sentence."""
        existed_clause = []
        for lit in clause:
            for c in self.l2c_all[lit]:
                existed_clause.append(set(c))
        if set(clause) in existed_clause:
            return True
        else:
            return False


    def remove_c(self, var):
        """Remove clauses including literal var from sentence."""
        tmp_list = list(self.l2c_all[var])
        for clause in tmp_list:
            self.sentence.remove(clause)
            for lit in clause:
                self.l2c_all[lit].remove(clause)
                self.num_lit[lit] -= len(clause)
