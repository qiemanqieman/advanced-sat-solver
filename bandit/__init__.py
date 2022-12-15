from .UCB import UCB

__all__ = {
    "init_bandit",
}


def init_bandit(sentence, alpha, discount, batch, bandit):
    if bandit is None:
        return None
    elif bandit.lower() == "ucb":
        return UCB(sentence, alpha, discount, batch)
