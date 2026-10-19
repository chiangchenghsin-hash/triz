"""Input generator: random small policy + random request (Cedar-semantics toy).

policy rules: (effect, principal, action), effect in {permit, forbid}.
principal/action support the "*" wildcard.
"""
import random


def gen(rng: random.Random):
    rules = []
    for _ in range(rng.randint(0, 4)):
        rules.append((
            rng.choice(["permit", "forbid"]),
            rng.choice(["alice", "bob", "*"]),
            rng.choice(["read", "write", "delete"]),
        ))
    return {
        "policy": rules,
        "principal": rng.choice(["alice", "bob"]),
        "action": rng.choice(["read", "write", "delete"]),
    }
