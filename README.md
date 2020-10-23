# pyAspic

pyAspic is a Python library for creating and evaluating ASPIC+ Argumentation Theories (Prakken, 2010).

## Getting started

The easiest way to use the library is to install via pip:

```pip install https://github.com/arg-tech/py-aspic.git@master#egg=pyaspic```

## Using the library

Note: this section assumes some knowledge of the principles in (Prakken, 2010)

To import the library:

``import pyaspic``

The library consists of the three main components of ASPIC+: *Argumentation System*, *Knowledge Base* and *Argumentation Theory*.

### Argumentation System

``system = pyaspic.ArgumentationSystem()``

An Argumentation System contains:

- a set of (strict and defeasible) rules
- a preference ordering over defeasible rules
- contrariness definitions between non-axiom formulae of the knowledge base

#### Rules

Rules can be constructed natively using the ``pyaspic.Rule`` class, or from a string representation.

The ``pyaspic.Rule`` class has a constructor of the form:

``Rule(label:str, antecedents:list, consequent:str, type:str)``

where ``type`` is ``pyaspic.Rule.STRICT`` or ``pyaspic.Rule.DEFEASIBLE``.

For instance:

``r1 = pyaspic.Rule("[r1]", ["a","b"], "c", pyaspic.Rule.STRICT)``

represents a strict rule with antecedents "a" and "b" and consequent "c".

Alternatively, ``pyaspic.Rule`` contains a static ``from_string`` method:

``pyaspic.Rule.from_string(label:str, rule:str)``

where ``rule`` is of the form:

``antecedent(,antecedent)+ (=>|->) consequent``

where ``=>`` represents a defeasible rule and ``->`` represents a strict rule.

For instance:

``r2 = pyaspic.Rule.from_string("[r2]", "d,e=>f")``

represents a defeasible rule with antecedents "d" and "e" and consequent "f".

#### Rule preference ordering

To add a preference between two defeasible rules, use the ``add_rule_preference`` method of ``pyaspic.ArgumentationSystem``:

``pyaspic.ArgumentationSystem.add_rule_preference(preference:tuple)``

where ``preference`` is a tuple of the form ``("label_of_less_preferred_rule", "label_of_more_preferred_rule")``

For instance:

``system.add_rule_preference(("[r1]","[r2]"))``

adds a preference where the rule [r1] is less preferred to the rule [r2].

### Knowledge Base

A Knowledge Base contains:

- a set of axioms, (ordinary) premises and assumptions
- a preference ordering over premises

An Argumentation Theory contains:

- an Argumentation System
- a Knowledge Base


```
from pyaspic import *

if __name__ == "__main__":
    system = ArgumentationSystem()
    kb = KnowledgeBase()

    kb.add_premise(Formula("a"))
    kb.add_premise(Formula("b"))

    system.add_rule(Rule.from_string("[r1]", "a->c"))
    system.add_rule(Rule.from_string("[r2]", "b=>d"))
    system.add_contrary(("d","c"))


    theory = ArgumentationTheory(system, kb)

    print(str(theory.check_well_formed()))

    result = theory.evaluate()
    print(result["acceptableConclusions"])

```



## References

Prakken, H. (2010). An abstract framework for argumentation using structured arguments.
*Argument & Computation*, 1(2), pp.93-124.
