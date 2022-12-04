from .NiVER import NiVER


__all__ = {
    "init_preprocess_policy",
    "after_assignment"
}


def init_preprocess_policy(preprocess_policy, sentence, num_vars):
    """Preprocess."""
    if preprocess_policy is None or preprocess_policy == "None":
        return None
    elif preprocess_policy.lower() == 'niver':
        return NiVER(sentence, num_vars)

    else:
        raise ValueError('Unknown preprocess policy: {}'.format(preprocess_policy))


def after_assignment(removed_clause, res):
    while len(removed_clause) != 0:
        lit, clause_list = removed_clause.pop()
        for clause in clause_list:
            flag = True
            for l in clause:
                if abs(l) != abs(lit) and l in res:
                    flag = False
                    break
            if flag:
                for l in clause:
                    if abs(l) == abs(lit):
                        if lit in res:
                            res.remove(lit)
                        elif -lit in res:
                            res.remove(-lit)
                        res.append(l)
                        break
    return res
