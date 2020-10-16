from .rule import Rule
from .formula import Formula

class ArgumentationSystem:

    def __init__(self, transposition=False):
        self.language = set()
        self.rules = set()
        self.rule_preferences = []

        self.contrariness = {}

        self.transposition = transposition

    def add_rule(self, rule:Rule):
        self.rules.add(rule)

        # if the rule is strict and we're closed under transposition, add the transposition
        if rule.type == Rule.STRICT and self.transposition == True:
            antecedents = [str(a) for a in rule.antecedents]

            label = rule.label[1:-1]

            new_antecedents = []
            skip = 0

            if len(antecedents) == 1:
                new_antecedents.append(["~"+str(rule.consequent)])
            else:
                while skip < len(antecedents):
                    s = []
                    for i in range(len(antecedents)):
                        if i != skip:
                            s.append(antecedents[i])

                    skip = skip + 1
                    if s:
                        s.append("~"+str(rule.consequent))
                        new_antecedents.append(s)

            counter = 1

            for s in new_antecedents:
                consequent = "~"+list(set(antecedents) - set(s))[0]
                new_rule = ",".join(s) + "->" + consequent
                new_label = "[{label}tp{counter}]".format(label=label,counter=str(counter))
                r = Rule.from_string(new_label, new_rule)
                self.rules.add(r)
                counter = counter + 1

    def add_rule_preference(self, preference):
        less_preferred = preference[0]
        more_preferred = preference[1]

        r = [rule for rule in self.rules if rule.label==less_preferred or rule.label==more_preferred and rule.type != Rule.STRICT]

        if len(r) == 2:
            self.rule_preferences.append(preference)

    def add_contrary(self, contrary, contradiction=False):
        '''
        Add a contrary to this system, where contrary = (el1, el2) is read as
        "el1 is a contrary of el2", or formally:
            el2 in cf(el1)

        If contradiction=True, el2 is also a contrary of el1, or formally:
            el1 in cf(el2)
        '''

        el1 = contrary[0]
        el2 = contrary[1]

        if str(el2) not in self.contrariness:
            self.contrariness[str(el2)] = set()

        if type(el1) is str:
            el1 = Formula(el1)

        self.contrariness[str(el2)].add(el1)

        if contradiction:
            self.add_contrary((el2, el1), False)

    def instantiate_formula(self, formula):
        '''
        Instantiates the given formula using the language
        '''

        instantiated = []
        parameter_mapping = []

        if formula.has_variables():
            for wff in self.language:
                parameter_map = {}
                tmp = []
                if formula.term == wff.term and len(formula.parameters) == len(wff.parameters):
                    for i in range(len(formula.parameters)):
                        if formula.parameters[i] == wff.parameters[i] or formula.parameters[i].isupper():
                            tmp.append(wff.parameters[i])
                            if formula.parameters[i].isupper():
                                parameter_map[formula.parameters[i]] = wff.parameters[i]

                    if len(tmp) == len(formula.parameters):
                        instantiated.append(Formula("{term}({params})".format(term=formula.term,params=",".join(tmp))))
                        parameter_mapping.append(parameter_map)
        else:
            instantiated = [formula]
            parameter_mapping.append({})

        return dict(zip(instantiated, parameter_mapping))

    def update_contrariness(self):
        '''
        Updates the contrariness to reflect specific instantiations of rules
        '''

        temp = {}

        for wff in self.language:
            wff = str(wff)
            if wff[0] == "~":
                temp[wff] = [wff[1:]]
            else:
                temp[wff] = ["~"+wff]

        contrary_pairs = []

        for el, contraries in self.contrariness.items():
            contrary_pairs.extend([(c, el) for c in contraries])

        contrary_pairs = [(str(el2), el1) for el1,x in self.contrariness.items() for el2 in x]

        for (el1, el2) in contrary_pairs:
            el1 = Formula(el1)
            el2 = Formula(el2)

            el1_instantiations = self.instantiate_formula(el1)
            el2_instantiations = self.instantiate_formula(el2)

            for el2_instantiation, el2_mapping in el2_instantiations.items():
                c = set(["~"+str(el2_instantiation)])
                for el1_instantiation, el1_mapping in el1_instantiations.items():
                    if el1_mapping == el2_mapping:
                        c.add(str(el1_instantiation))
                    elif el1_mapping == {} or el2_mapping == {}:
                        c.add(str(el1_instantiation))
                    else:
                        for k1,v1 in el1_mapping.items():
                            add = True
                            for k2, v2 in el2_mapping.items():
                                if v1 == v2 and k1 != k2 or k1 == k2 and v1 != v2:
                                    add = False
                                    break
                            if add:
                                c.add(str(el1_instantiation))

                temp[str(el2_instantiation)] = c

        self.contrariness = temp
