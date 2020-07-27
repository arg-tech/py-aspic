

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
