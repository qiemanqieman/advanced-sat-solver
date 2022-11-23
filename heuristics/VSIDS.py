import bisect
from .heuristics import Heuristic


class VSIDS(Heuristic):
    def __init__(self, sentence, decay=0.95):
        self.decay = decay
        self.vsids_scores = self.init_vsids_scores(sentence)

    def init_vsids_scores(self, sentence):
        """Initialize variable scores for VSIDS.
        we need to design it to be in order(in my case, decreasing order), so that accelerate deciding"""
        scores = {}
        """ YOUR CODE HERE """
        for clause in sentence:
            for literal in clause:
                scores[literal] = scores.get(literal, 0) + 1
        return dict(sorted(scores.items(), key=lambda i: i[1], reverse=True))

    def update_vsids_scores(self, vsids_scores, learned_clause):
        """Update VSIDS scores.
        note that the sorting order should be maintained"""
        increased = []
        for lit in learned_clause:
            increased.append([(vsids_scores.pop(lit) + 1) * self.decay, lit])
        for lit in vsids_scores:
            vsids_scores[lit] = vsids_scores[lit] * self.decay
        scores = [[i[1], i[0]] for i in vsids_scores.items()]
        scores.reverse()
        for i in increased:
            bisect.insort(scores, i)  # use bisect method for accelerating the operation of maintaining order
        scores.reverse()
        scores = [(i[1], i[0]) for i in scores]
        scores = dict(scores)
        vsids_scores.clear()
        vsids_scores.update(scores)

    def after_confilct_analysis(self, learnt_clause_literals, conflict_side_literals):
        """Called after a learnt clause is generated from conflict analysis."""
        self.update_vsids_scores(self.vsids_scores, learnt_clause_literals)

    def on_assign(self, literal):
        """Called when a literal is assigned or propagated."""
        pass

    def on_unassign(self, literal):
        """Called when a literal is unassigned by backtracking or restart."""
        pass

    def decide(self, assigned):
        """Decide which variable to assign and whether to assign True or False.
        reset value to 0 for those have been assigned and reposition to the end so that new learned clause's literal will have
        more chance to be chosen"""
        for literal in self.vsids_scores:
            if literal not in assigned and -literal not in assigned:
                return literal
        return None

    def rearrange(self, unassigned_literals):
        """Rearrange the order of unassigned literals.
        This method is called after the solver has finished searching for a solution."""
        pass