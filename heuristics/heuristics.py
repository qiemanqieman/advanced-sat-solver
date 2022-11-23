"""
heuristics.py
define some algorithm/policy to decide which literal to be assigned next.
"""

from abc import ABC, abstractmethod


class Heuristic(ABC):
    """The abstract base class for all heuristic branching algorithm of CDCL SAT solver"""
    @abstractmethod
    def after_conflict_analysis(self, learnt_clause_literals, conflict_side_literals):
        """Called after a learnt clause is generated from conflict analysis."""
        pass

    @abstractmethod
    def on_assign(self, literal):
        """Called when a literal is assigned or propagated."""

    @abstractmethod
    def on_unassign(self, literal):
        """Called when a literal is unassigned by backtracking or restart."""
        pass

    @abstractmethod
    def decide(self, assigned):
        """decide which literal to be assigned next"""
        pass

    @abstractmethod
    def rearrange(self, unassigned_literals):
        pass
