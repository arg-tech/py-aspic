from .argument import *
from .argumentation_system import ArgumentationSystem
from .knowledge_base import KnowledgeBase
from .formula import Formula
import itertools
import copy
from .set_preference import check_preference
import requests
import json


import pprint

class ArgumentationTheory:
    '''
    Class representing an ASPIC+ Argumentation Theory (AT)
    '''

    def __init__(self, argumentation_system, knowledge_base, ordering="weakest"):
        self.argumentation_system = argumentation_system
        self.knowledge_base = knowledge_base

        self.arg_count = 0;

        self.arguments = []
        self.attack = []
        self.defeat = []

        self.argument_preferences = []
        self.ordering = ordering

    def check_well_formed(self):
        '''
        Checks if this theory is well-formed based on the two principles in Prakken 2010
        '''

        # check 1: no consequent of a defeasible rule is a contrary of the consequent of a strict rule
        rules = self.argumentation_system.rules
        contrariness = self.argumentation_system.contrariness

        # record the rule consequents for check 2...
        rule_consequents = []

        for r1 in rules:
            rule_consequents.append(r1.consequent)
            for r2 in rules:
                if r1.label == r2.label:
                    continue

                if r1.type == Rule.STRICT and r2.type == Rule.DEFEASIBLE:
                    if str(r1.consequent) in contrariness and str(r2.consequent) in contrariness[str(r1.consequent)]:
                        return False

        # check 2: assumptions can't be contraries of consequents of rules, nor axioms/premises
        for a in self.knowledge_base.assumptions:
            for el in rule_consequents + self.knowledge_base.axioms + self.knowledge_base.premises:
                if str(el) in contrariness:
                    if str(a) in contrariness[str(el)]:
                        return False

        return True


    def evaluate(self, semantics="grounded", query=None):

        self.construct_arguments()
        self.calculate_argument_preferences()
        self.calculate_defeat()


        url = "http://ws.arg.tech/e/dom"

        data = {
            "arguments": [a.label for a in self.arguments],
            "attacks": ["({a},{b})".format(a=a,b=b) for (a,b) in self.calculate_defeat()],
            "semantics": semantics
        }
        response = requests.post(url, data = json.dumps(data))
        response = response.json()

        if semantics not in response:
            semantics = "grounded"

        extensions = {i: response[semantics][i] for i in range(len(response[semantics])) if type(response[semantics][i]) is list }

        if not extensions:
            extensions = {0: response[semantics]}

        del response[semantics]
        response["extensions"] = extensions


        response["acceptableConclusions"] = {}

        for id, ext in extensions.items():
            response["acceptableConclusions"][id] = [str(a.conclusion) for a in self.arguments if a.label in extensions[id]]

        response["arguments"] = {}

        for a in self.arguments:
            arg = {"conclusion": str(a.conclusion),
                   "defeasible_rules": [str(r) for r in a.defeasible_rules],
                   "premises": [str(p) for p in a.premises],
                   "top_rule": str(a.top_rule),
                   "sub_arguments": [s.label for s in a.sub_arguments],
                   "last_sub_arguments": [s.label for s in a.last_sub_arguments]
                  }
            response[a.label] = arg


        return response


    def calculate_argument_preferences(self):
        '''
        Calculates the argument preferences based on the ordering provided at construction time,
        and the preferences between knowledge base elements and/or rules
        '''

        self.argument_preferences = []

        for arg1 in self.arguments:
            for arg2 in self.arguments:
                if arg1.label == arg2.label:
                    continue

                if self.ordering == "last":
                    if (arg1.is_strict() and arg1.is_firm()) and (arg2.is_defeasible() or arg2.is_plausible()):
                        self.argument_preferences.append((arg2.label, arg1.label))
                    elif not arg1.last_def_rules() and not arg2.last_def_rules():
                        if check_preference(arg1.premises, arg2.premises, self.knowledge_base.preferences):
                            self.argument_preferences.append((arg1.label, arg2.label))
                    elif check_preference(arg1.last_def_rules(), arg2.last_def_rules(), self.argumentation_system.rule_preferences):
                            self.argument_preferences.append((arg1.label, arg2.label))
                elif self.ordering == "weakest":
                    if check_preference(arg1.premises, arg2.premises, self.knowledge_base.preferences):
                        if arg2.defeasible_rules:
                            if check_preference(arg1.get_defeasible_rules(), arg2.get_defeasible_rules(), self.argumentation_system.rule_preferences):
                                self.argument_preferences.append((arg1.label, arg2.label))
                        else:
                            self.argument_preferences.append((arg1.label, arg2.label))

        return self.argument_preferences


    def calculate_defeat(self):
        '''
        Calculates defeat by considering attacks and preferences

        Takes advantage of the recursive nature of the calculate_attack method
        by first calculating simple attacks, filtering these into defeats
        then passing the filtered list into the calculate_attack method
        '''

        att = self.calculate_attack(simple=True)

        prefs = self.calculate_argument_preferences()
        defeat = []

        for (arg1, arg2) in att:
            if (arg1, arg2) in prefs and (arg2, arg1) in prefs:
                defeat.append((arg1,arg2))
            elif(arg2, arg1) in prefs:
                defeat.append((arg1, arg2))

        self.defeat = self.calculate_attack(attacks=defeat)
        return self.defeat

    def calculate_attack(self, attacks=None, simple=False):
        '''
        Calculates attack based on contrariness and undercutting rules
        If simple == True then only direct attacks based on the contrariness and undercutters
        are considered;
        If simple == False, then all attacks are (recursively) calculated
        (i.e. if A attacks B and B is a sub-argument in C, then A will attack C)
        '''

        if attacks is None:
            attacks = []
            for arg1 in self.arguments:

                # arguments whose top rules are strict cannot be attacked
                if arg1.top_rule is not None and arg1.top_rule.type == Rule.STRICT:
                    continue
                arg1_conclusion = str(arg1.conclusion)

                if arg1_conclusion in self.argumentation_system.contrariness:
                    contraries = self.argumentation_system.contrariness[arg1_conclusion]

                    for arg2 in self.arguments:
                        arg2_conclusion = str(arg2.conclusion)
                        if arg2_conclusion in contraries:
                            attacks.append((arg2.label, arg1.label))
                elif arg1_conclusion[:2] == "~[":
                    undercut_rule = arg1_conclusion[1:]
                    for arg2 in self.arguments:
                        if arg2.top_rule:
                            if arg2.top_rule.type==Rule.DEFEASIBLE and arg2.top_rule.label == undercut_rule:
                                attacks.append((arg1.label,arg2.label))
            if simple:
                return attacks
            else:
                return self.calculate_attack(attacks)
        else:
            tmp_attacks = [a for a in attacks]

            for (arg1, arg2) in tmp_attacks:
                for arg in self.arguments:
                    if arg2 in [a.label for a in arg.sub_arguments]:
                        att = (arg1, arg.label)
                        if att not in attacks:
                            attacks.append(att)

            if len(attacks) == len(tmp_attacks):
                return attacks
            else:
                return self.calculate_attack(attacks)

    def construct_arguments(self, args=None):
        '''
        Recursively constructs arguments by:
            1) constructing atomic arguments based on the knowledge base
            2) constructing arguments based on the atomic arguments and the rules
            3) repeatedly trying to construct more arguments until no more can be found
        '''

        if args is not None:
            tmp_args = [a for a in args]
        else:
            tmp_args = None

        if tmp_args is None:
            tmp_args = []
            for p in self.knowledge_base.premises + self.knowledge_base.axioms + self.knowledge_base.assumptions:
                self.arg_count = self.arg_count + 1
                a = AtomicArgument("A" + str(self.arg_count), p)
                if a.conclusion.term[:2] != "~[":
                    self.argumentation_system.language.add(a.conclusion)
                tmp_args.append(a)

            self.arguments = self.construct_arguments(tmp_args)
            return self.arguments
        else:
            # get all the used defeasible rules - used to determine if undercutters are relevant
            used_defeasible_rules = set([r.label for a in tmp_args for r in a.defeasible_rules])

            for r in self.argumentation_system.rules:
                if r.is_undercutter:
                    label = r.consequent.term[1:].strip()
                    if label not in used_defeasible_rules:
                        continue # don't consider this rule if the rule it undercuts isn't used

                antecedent_fulfilment = {}

                parameter_mapping = {}
                comparisons = []

                for ant in r.antecedents:

                    if "<" in ant.term or ">" in ant.term or "=" in ant.term:
                        comparisons.append(ant)
                        continue

                    for a in args:
                        # don't re-use rules
                        if r.label in [rule.label for rule in a.rules]:
                            continue

                        conclusion = a.conclusion
                        tmp = []

                        ''' Only consider this conclusion as fulfilling the antecedent
                            if it has the same term and same number of parameters'''
                        if conclusion.term == ant.term and len(conclusion.parameters) == len(ant.parameters):
                            for i in range(len(conclusion.parameters)):
                                ''' either the paramters are the same, or the antecedent has a variable in this position'''
                                if conclusion.parameters[i] == ant.parameters[i] or ant.parameters[i][0].isupper():
                                    tmp.append(conclusion.parameters[i])
                                    if str(conclusion) not in parameter_mapping:
                                        parameter_mapping[str(conclusion)] = {}

                                    ''' and if the antecedent does have a  variable, record the value it should be mapped to '''
                                    if ant.parameters[i][0].isupper():
                                        parameter_mapping[str(conclusion)][ant.parameters[i][0]] = conclusion.parameters[i]

                            '''if the temporary list is the same length as the antecedent paramters, this conclusion fulfils it'''
                            if len(tmp) == len(ant.parameters):
                                if ant.term not in antecedent_fulfilment:
                                    antecedent_fulfilment[ant.term] = []
                                antecedent_fulfilment[ant.term].append(a)

                t = [s for s in antecedent_fulfilment.values()]

                ''' from here, consider only relevant antecedents: those that are fulfilled by the conclusions
                    of other arguments, rather than those that express an arthimetic comparison'''
                relevant_antecedents = [a for a in r.antecedents if a.term not in [c.term for c in comparisons]]

                ''' only continue if every antecedent has at least one argument that fulfils it '''
                if set(antecedent_fulfilment.keys()) == set([a.term for a in relevant_antecedents]):

                    ''' create the cartesian product from each set of fulfilling arguments;
                        this provides full coverage of all possible combinations of args to instantiate this rule'''
                    for argument_sets in itertools.product(*t):
                        argument_sets = list(argument_sets)

                        proceed = True
                        ''' verify parameters: we can only continue if the parameter mappings harmonise (see harmonise_parameters method)'''
                        harmonised_parameters = self.harmonise_parameters(argument_sets, parameter_mapping)

                        if harmonised_parameters is None:
                            continue

                        # do we have any comparisons that need evaluated
                        for comparison in comparisons:
                            result = comparison.evaluate_comparison(harmonised_parameters)
                            if not result:
                                proceed = False
                                break

                        if not proceed:
                            continue

                        if r.consequent.has_variables():
                            new_rule = copy.deepcopy(r)
                            for a in argument_sets:
                                if str(a.conclusion) in parameter_mapping:
                                    map = parameter_mapping[str(a.conclusion)]

                                    parameters = new_rule.consequent.parameters
                                    variables = new_rule.consequent.variables

                                    for i in range(len(variables)):
                                        if variables[i] in map:
                                            for a in new_rule.antecedents:
                                                a.variable_mapping[variables[i]] = map[variables[i]]
                                            new_rule.consequent.variable_mapping[variables[i]] = map[variables[i]]

                                    new_rule.consequent.resolve_expressions()

                                    for i in range(len(parameters)):
                                        if parameters[i] in map:
                                            new_rule.consequent.parameters[i] = map[parameters[i]]
                        else:
                            new_rule = r

                        self.arg_count = self.arg_count + 1
                        a = RuleArgument("A" + str(self.arg_count), new_rule, argument_sets)
                        if a.conclusion.term[:2] != "~[":
                            self.argumentation_system.language.add(a.conclusion)

                        if a not in args:
                            args.append(a)
                        else:
                            self.arg_count = self.arg_count - 1

            ''' anchor step; if True, we haven't added more args in this pass so should return'''
            if len(args) == len(tmp_args):

                # update contrariness
                self.argumentation_system.update_contrariness()
                return args
            else:
                return self.construct_arguments(args)



    def harmonise_parameters(self, arguments, parameter_mapping):
        '''
        Attempts to generate a harmonised parameter mapping based on the mappings
        for individual arguments (i.e. X in arg1 must be mapped to the same value as X in arg2, or not exist in arg2 etc.)
        '''

        harmonised_parameters = {}
        proceed = True

        if len(arguments) > 1:
            for arg in arguments:
                conclusion = str(arg.conclusion)
                if conclusion in parameter_mapping:
                    for parameter,value in parameter_mapping[conclusion].items():
                        for arg2 in arguments:
                            conclusion2 = str(arg2.conclusion)
                            if conclusion != conclusion2 and conclusion2 in parameter_mapping:
                                if parameter in parameter_mapping[conclusion2] and parameter_mapping[conclusion2][parameter] != value:
                                    proceed = False
                                    harmonised_parameters = None
                                    break
                                else:
                                    harmonised_parameters[parameter] = value
                                if not proceed:
                                    break
                if not proceed:
                    break
        else:
            harmonised_parameters = parameter_mapping[str(arguments[0].conclusion)]

        return harmonised_parameters

if __name__ == "__main__":
    system = ArgumentationSystem()
    kb = KnowledgeBase()

    kb.add_premise(Formula("current_goal(steps)"))
    kb.add_premise(Formula("user_age(17)"))
    kb.add_premise(Formula("rejected_too_high(13000)"))


    system.add_rule(Rule.from_string("[r1]", "current_goal(steps) => recommended(10000)"))
    system.add_rule(Rule.from_string("[r2]", "recommended(X) => set_goal(X)"))
    system.add_rule(Rule.from_string("[r3]", "current_goal(steps), user_age(X), X>65 => suggested(7500)"))
    system.add_rule(Rule.from_string("[r4]", "current_goal(steps), user_age(X), X<18 => suggested(13000)"))
    system.add_rule(Rule.from_string("[r5]", "suggested(X), => set_goal(X)"))
    system.add_rule(Rule.from_string("[r6]", "rejected_too_high(X) -> ~set_goal(X)"))
    system.add_rule(Rule.from_string("[r7]", "rejected_too_low(X) -> ~set_goal(X)"))
    system.add_rule(Rule.from_string("[r8]", "rejected_too_high(X) => suggested([X*0.8])"))
    system.add_rule(Rule.from_string("[r9]", "rejected_too_low(X) => suggested([X*1.2])"))

    print([str(r) for r in system.rules])

    system.add_contrary((Formula("set_goal(X)"), Formula("set_goal(Y)")), True)
    system.add_rule_preference(("[r2]","[r5]"))
    system.add_rule_preference(("[r2]","[r8]"))
    system.add_rule_preference(("[r2]","[r9]"))

    theory = ArgumentationTheory(system, kb)

    result = theory.evaluate()
    print(result)
