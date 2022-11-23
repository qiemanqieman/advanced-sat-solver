# from queue import PriorityQueue as PQ
# from binarysearchtree import BST
import bisect


class LRB:
    def __init__(self, sentence, alpha=0.4):
        self.alpha = alpha
        self.learn_counter = 0
        self.ema, self.assigned_at, self.participated_in = {}, {}, {}
        for clause in sentence:
            for literal in clause:
                self.ema[literal] = 0.0
                self.assigned_at[literal] = 0
                self.participated_in[literal] = 0
                # self.assigned[literal] = False

    def after_confilct_analysis(self, learnt_clause_literals, conflict_side_literals):
        """Called after a learnt clause is generated from conflict analysis."""
        self.learn_counter += 1
        self.alpha = max(0.06, self.alpha - 1e-6)
        # need_update = []
        for literal in learnt_clause_literals:
            self.participated_in[literal] += 1
            # self.ema.pop(literal)
            # need_update.append([self.participated_in.pop(literal) + 1, literal])
        for literal in conflict_side_literals:
            self.participated_in[literal] += 1
            # self.ema.pop(literal)
            # need_update.append([self.participated_in.pop(literal) + 1, literal])
        # scores = [[i[1], i[0]] for i in self.ema.items()]
        # scores.reverse()
        # for i in need_update:
        #     bisect.insort(scores, i)  # use bisect method for accelerating the operation of maintaining order
        # scores.reverse()
        # scores = [(i[1], i[0]) for i in scores]
        # # scores_1 = dict(scores)
        # self.ema.clear()
        # self.ema.update(scores)

    def on_assign(self, literal):
        """Called when a literaliable is assigned or propagated."""
        self.assigned_at[literal] = self.learn_counter
        self.participated_in[literal] = 0
        # self.assigned[literal] = True

    def on_unassign(self, literal):
        """Called when a literal is unassigned by backtracking or restart."""
        interval = self.learn_counter - self.assigned_at[literal]
        if interval > 0:
            reward = float(self.participated_in[literal]) / interval
            self.ema[literal] = self.alpha * reward + (1 - self.alpha) * self.ema[literal]
        # self.assigned[literal] = False

    def decide(self, assigned):
        for literal in self.ema:
            # if not self.assigned[literal] and not self.assigned[-literal]:
            if literal not in assigned and -literal not in assigned:
                return literal
        return None

    def rearrange(self, unassigned_literals):
        need_adjust_order = []
        for lit in unassigned_literals:
            need_adjust_order.append([self.ema.pop(lit), lit])
        scores = [[i[1], i[0]] for i in self.ema.items()]
        scores.reverse()
        for i in need_adjust_order:
            bisect.insort(scores, i)  # use bisect method for accelerating the operation of maintaining order
        scores.reverse()
        scores = [(i[1], i[0]) for i in scores]
        self.ema.clear()
        self.ema.update(scores)
