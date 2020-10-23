"""
Copyright (C) 2020  Centre for Argument Technology (http://arg.tech)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

class KnowledgeBase:

    AXIOM = "axiom"
    PREMISE = "premise"
    ASSUMPTION = "assumption"


    def __init__(self):
        self.axioms = []
        self.premises = []
        self.assumptions = []

        self.preferences = []

    def add_axiom(self, formula):
        self.axioms.append(Axiom(formula))

    def add_premise(self, formula):
        self.premises.append(Premise(formula))

    def add_assumption(self, formula):
        self.assumptions.append(Assumption(formula))

    def add_preference(self, preference):
        lp = str(preference[0])
        mp = str(preference[1])

        str_axioms = [str(a) for a in self.axioms]
        str_premises = [str(p) for p in self.premises]
        str_assumptions = [str(a) for a in self.assumptions]

        if lp in str_axioms or mp in str_axioms:
            return

        if lp in str_premises and mp in str_assumptions:
            return

        self.preferences.append((lp, mp))

class KnowledgeBaseElement:

    def __init__(self):
        self.type = None
        self.formula = None

    def __str__(self):
        return self.formula.__str__()

    # def __repr__(self):
    #     return self.formula

class Axiom(KnowledgeBaseElement):

    def __init__(self, formula):
        self.type = KnowledgeBase.AXIOM
        self.formula = formula
        self.term = formula.term
        self.parameters = formula.parameters

class Premise(KnowledgeBaseElement):

    def __init__(self, formula):
        self.type = KnowledgeBase.PREMISE
        self.formula = formula
        self.term = formula.term
        self.parameters = formula.parameters

class Assumption(KnowledgeBaseElement):

    def __init__(self, formula):
        self.type = KnowledgeBase.ASSUMPTION
        self.formula = formula
        self.term = formula.term
        self.parameters = formula.parameters
