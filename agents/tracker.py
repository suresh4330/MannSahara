"""Multi-turn risk tracker with crisis latch and configurable persistence rules.
Implements T0 (latch), T1 (persistence: M of last W turns >= 1 -> Level 2),
and T2 (repetition: N turns of Level 2 -> Level 3 latched).
"""


class RiskTracker:
    def __init__(self, mild_in_window: int = 3, window: int = 4, level2_to_crisis: int = 3):
        self.m = mild_in_window
        self.w = window
        self.n = level2_to_crisis
        self.reset()

    def reset(self):
        self.history = []
        self.latched = False

    def update(self, score: int) -> int:
        self.history.append(score)
        if self.latched or score >= 3:
            self.latched = True
            return 3

        level = score
        # T1 persistence: if at least M of the last W turns score >= 1, effective level is at least 2
        if sum(1 for s in self.history[-self.w:] if s >= 1) >= self.m:
            level = max(level, 2)

        # T2 repetition: if N turns have scored exactly 2, effective level becomes 3 (latched)
        if sum(1 for s in self.history if s == 2) >= self.n:
            self.latched = True
            return 3

        return level

