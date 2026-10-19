"""Small model (reference semantics): forbid_trumps_permit.

Any request matching a forbid rule must be denied. This is the executable
statement of the property; in a real project it corresponds to the Lean
small model.
"""


def run(inp):
    principal, action = inp["principal"], inp["action"]

    def hit(rule):
        effect, who, act = rule
        return (who == principal or who == "*") and act == action

    # Core of the property: scan forbid first; a hit denies even if a
    # permit also matches.
    for rule in inp["policy"]:
        if rule[0] == "forbid" and hit(rule):
            return "deny"
    for rule in inp["policy"]:
        if rule[0] == "permit" and hit(rule):
            return "allow"
    return "deny"  # default deny
