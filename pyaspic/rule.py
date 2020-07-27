import re
from .formula import Formula

class Rule:

    DEFEASIBLE = "=>"
    STRICT = "->"

    def __init__(self, label, antecedents, consequent, type):
        self.antecedents = antecedents
        self.consequent = consequent
        self.type = type
        self.label = label

        if consequent.term[:2] == "~[":
            self.is_undercutter = True
        else:
            self.is_undercutter = False

    def from_string(label, str_):
        if Rule.DEFEASIBLE in str_:
            type = Rule.DEFEASIBLE
        elif Rule.STRICT in str_:
            type = Rule.STRICT
        else:
            return None

        antecedent_regex = r"([^(), ]+\([^()]+\)?|[^(), ]+)"

        parts = str_.split(type)

        antecedents = [Formula(a.strip()) for a in re.findall(antecedent_regex, parts[0].strip())]
        consequent = Formula(parts[1].strip())


        r = Rule(label, antecedents, consequent, type)
        return r

    def __str__(self):
        return "{label} {ants}{arrow}{cons}".format(label=self.label,ants=",".join([str(a) for a in self.antecedents]),arrow=self.type,cons=self.consequent)

    def __eq__(self, other):
        if self.antecedents == other.antecedents and self.consequent == other.consequent and self.type == other.type:
            return True
        else:
            return False

    def __hash__(self):
        return hash("".join([str(a) for a in self.antecedents]) + str(self.consequent) + str(self.type))


if __name__ == "__main__":
    Rule.from_string("[r1]","foo(X),too(Y)=>bar(X,Y)")
