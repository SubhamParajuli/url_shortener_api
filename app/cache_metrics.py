"""
small class to keep track how many time redis cache hit or miss.
just in-memory counter, not saved anywhere permanent (reset when
app restart).
"""

class CacheMetrics:
    """
    holds hits/misses counter and give hit_rate percentage.
    """
    def __init__(self):
        self.hits=0
        self.misses=0


    @property
    def hit_rate(self):
        """
        calculate percentage of hit out of total request, avoid
        divide by zero if no request yet.
        """
        total=self.hits +self.misses

        if total==0:
            return 0.0

        return self.hits/total


# single shared object, import this same instance everywhere so counter stay consistent
cache_metrics=CacheMetrics()
