"""Production implementation with a seeded classic bug: permit is checked
before forbid.

When a policy matches both a permit and a forbid rule, this implementation
returns allow — violating forbid_trumps_permit. Differential testing should
catch it.
"""


def run(inp):
    principal, action = inp["principal"], inp["action"]

    def hit(rule):
        effect, who, act = rule
        return (who == principal or who == "*") and act == action

    # BUG: permit short-circuits forbid
    for rule in inp["policy"]:
        if rule[0] == "permit" and hit(rule):
            return "allow"
    for rule in inp["policy"]:
        if rule[0] == "forbid" and hit(rule):
            return "deny"
    return "deny"
