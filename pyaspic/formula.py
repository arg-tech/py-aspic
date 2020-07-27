import re

class Formula:

    def __init__(self, str_formula):
        self.regex = re.compile(r"(([^() ]+)(\([^()]+\))?)", re.VERBOSE)

        self.comparison_regex = re.compile(r"((?:[A-Z][a-z]*)|(?:[0-9]+))[ ]*(?:<|>|==)[ ]*([A-Z][a-z]*|[0-9]+)")

        self.expression_regex = re.compile(r"\[([^\[\]]+)\]")

        self.expressions = {}
        self.expression_map = {}

        self.variable_mapping = {}

        self.is_comparison = False

        match = re.findall(self.regex, str_formula)

        if match:
            match = [m for m in match[0] if m.strip() != '']

            self.term = match[1]

            self.parameters = []
            self.variables = []

            if len(match) == 3:
                for v in match[2][1:-1].split(","):
                    v = v.strip()
                    if not self.parse_expression(v):
                        self.parameters.append(v)
                        if v[0].isupper():
                            self.variables.append(v)
            else:
                match2 = re.findall(self.comparison_regex, self.term)
                if match2:
                    self.is_comparison = True
                    for m in match2[0]:
                        if m[0].isupper():
                            self.variables.append(m[0])

    def has_variables(self):
        return (len(self.variables) > 0)


    def evaluate_comparison(self, variable_mapping):
        if not self.is_comparison:
            return False

        expression = self.term

        for k,v in variable_mapping.items():
            expression = expression.replace(k,v)

        try:
            result = eval(expression)
        except:
            result = False

        return result


    def parse_expression(self, input):
        match = re.findall(self.expression_regex, input)

        if match:
            expr_parameters = []
            current = ""
            self.parameters.append(match[0])
            for char in match[0]:
                if char in ["+","-","*","/","{","}"]:
                    if current != "":
                        if current[0].isupper():
                            self.variables.append(current)
                            expr_parameters.append(current)
                    current = ""
                else:
                    current = current + char
            if current != "":
                if current[0].isupper():
                    self.variables.append(current)
                    expr_parameters.append(current)

            expr = match[0].replace("{","(")
            expr = expr.replace("}",")")

            self.expressions[len(self.parameters)-1] = {"parameters": expr_parameters, "expression": expr}
            self.expression_map[match[0]] = match[0]

            return True
        else:
            return False


    def resolve_expressions(self):
        for k,v in self.expressions.items():
            parameters = v["parameters"]
            expression = v["expression"]

            for p in v["parameters"]:
                if p in self.variable_mapping:
                    value = self.variable_mapping[p]
                    expression = expression.replace(p, value)

            try:
                result = int(eval(expression))
            except:
                result = 0

            self.parameters[k] = str(result)

    def __str__(self):
        if self.parameters:

            p = []
            for param in self.parameters:
                if param in self.expression_map:
                    p.append("[{expr}]".format(expr=self.expression_map[param]))
                elif param in self.variable_mapping:
                    p.append(self.variable_mapping[param])
                else:
                    p.append(param)


            return "{term}({parameters})".format(term=self.term, parameters=", ".join(p))
        else:
            return str(self.term)

    # def __repr__(self):
    #     return self.__str__()

    def __eq__(self, other):
        if self.term == other.term and self.parameters == other.parameters:
            return True
        else:
            return False

    def __hash__(self):
        return hash(str(self.term) + str(self.parameters))
