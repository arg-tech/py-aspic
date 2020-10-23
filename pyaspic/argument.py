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

from .rule import Rule
from .formula import Formula
from .knowledge_base import KnowledgeBase

class Argument:

    def __init__(self, label, conclusion):

        self.label = label
        self.conclusion = conclusion
        self.premises = []
        self.sub_arguments = []
        self.last_sub_arguments = []
        self.rules = []
        self.defeasible_rules = []
        self.strict_rules = []
        self.acceptable = False


    def is_strict(self):
        return (len(self.defeasible_rules) == 0)

    def is_defeasible(self):
        return not self.is_strict()

    def is_firm(self):
        axioms = [a for a in self.premises if a.type==KnowledgeBase.AXIOM]

        return (len(axioms) > 0)

    def is_plausible(self):
        return not self.is_firm()


    def last_def_rules(self):
        if self.top_rule:
            if self.top_rule.type == Rule.DEFEASIBLE:
                return [self.top_rule.label]

        return []

    def get_defeasible_rules(self):
        return [r.label for r in self.defeasible_rules]


    # def __repr__(self):
    #     if self.sub_arguments:
    #         return self.label + ": " + ",".join([a.label for a in self.last_sub_arguments]) + self.top_rule.type + str(self.conclusion)
    #     else:
    #         return "{label}: {conclusion}".format(label=self.label,conclusion=str(self.conclusion))

    def __str__(self):
        if self.sub_arguments:
            return self.label + ": " + ",".join([a.label for a in self.last_sub_arguments]) + self.top_rule.type + str(self.conclusion)
        else:
            return "{label}: {conclusion}".format(label=self.label,conclusion=str(self.conclusion))

    def __hash__(self):
        return hash("".join([str(a) for a in self.sub_arguments]) + "".join([str(r) for r in self.rules]))

    def __eq__(self, other):
        return self.__hash__() == other.__hash__();


class AtomicArgument(Argument):

    def __init__(self, label, proposition):
        super().__init__(label, proposition)

        self.premises.append(proposition)
        self.top_rule = None

class RuleArgument(Argument):
    def __init__(self, label, top_rule, last_sub_arguments):
        super().__init__(label, top_rule.consequent)

        self.last_sub_arguments = last_sub_arguments
        self.rules.append(top_rule)

        for a in last_sub_arguments:
            self.premises.extend(a.premises)
            self.rules.extend([r for r in a.rules if r not in self.rules])
            self.sub_arguments.extend([a] + a.sub_arguments)

        self.defeasible_rules = [r for r in self.rules if r.type==Rule.DEFEASIBLE]
        self.strict_rules = [r for r in self.rules if r.type==Rule.STRICT]

        self.top_rule = top_rule
