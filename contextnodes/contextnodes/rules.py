"""Rules example:
# 'context': (variable, value, exclude)
[
    {
        'use': True,
        'context': ('shots', '10:10-30;20'),
        'mode': 'include'
    },
    {
        'use': True,
        'context': ('shots', '010_0010'),
        'mode': 'exclude'
    }
]
"""

import json
import nuke
from contextnodes.knobs import CONTEXT_RULES


def build_rule_data(
        variable: str,
        value: str,
        use: bool = True,
        mode: str = 'include') -> dict:
    data = dict(use=use, context=(variable, value), mode=mode)
    return data


def get_rules(node: nuke.Node) -> list[dict] | None:
    if CONTEXT_RULES not in node.knobs():
        return
    if rules := node[CONTEXT_RULES].value():
        rules = json.loads(rules)
        return rules


def update_rules(node: nuke.Node, data: list[dict] | dict):
    rules = get_rules(node) or []
    if isinstance(data, dict):
        rules.append(data)
    elif isinstance(data, list):
        rules = data
    node[CONTEXT_RULES].setValue(json.dumps(rules))


def find_rule(rules: list, variable: str) -> tuple[int, dict] | None:
    for index, rule in enumerate(rules):
        context_variable, _ = rule['context']
        if context_variable == variable:
            return index, rule
