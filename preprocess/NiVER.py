

class NiVER:
    """Preprocess based on Non Increasing VER (NiVER)"""

    def __init__(self, sentence, num_vars):

        self.sentence = sentence
        self.num_vars = num_vars
        self.l2c_all = self._init_watch()
        self.removed_clause = []

    def preprocess(self):
        while True:
            entry = False
            for var in range(1, self.num_vars + 1):
                if var % 100 == 0:
                    print(var)
                if len(self.l2c_all[var]) == 0 or len(self.l2c_all[-var]) == 0:
                    continue
                R_clause_set = []
                old_num_lit, new_num_lit = 0, 0
                for N_clause in self.l2c_all[-var]:
                    old_num_lit += len(N_clause)
                for P in self.l2c_all[var]:
                    old_num_lit += len(P)
                    for N in self.l2c_all[-var]:
                        P_clause = list(P)
                        N_clause = list(N)
                        P_clause.remove(var)
                        N_clause.remove(-var)
                        new_clause = list(set(P_clause + N_clause))
                        if len(new_clause) == 0:
                            return None, None
                        flag = True
                        for lit in new_clause:
                            if -lit in new_clause:
                                flag = False
                                break
                        if flag and new_clause not in self.sentence:
                            new_num_lit += len(new_clause)
                            R_clause_set.append(new_clause)
                if old_num_lit >= new_num_lit:
                    self.removed_clause.append((var, self.l2c_all[var] + self.l2c_all[-var]))
                    self.remove_clause(var)
                    self.remove_clause(-var)
                    for clause in R_clause_set:
                        self.sentence.append(clause)
                        for lit in clause:
                            self.l2c_all[lit].append(clause)
                    entry = True
                # print(sentence)
            if not entry:
                break
        return self.sentence, self.removed_clause

    def _init_watch(self):
        l2c_all = {}
        for i in range(-self.num_vars, self.num_vars + 1):
            l2c_all[i] = []
        for clause in self.sentence:
            for lit in clause:
                l2c_all[lit].append(clause)
        return l2c_all

    def remove_clause(self, var):
        tmp_list = list(self.l2c_all[var])
        for clause in tmp_list:
            self.sentence.remove(clause)
            for lit in clause:
                self.l2c_all[lit].remove(clause)
