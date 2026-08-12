class CacheMetrics:
    def __init__(self):
        self.hits=0
        self.misses=0


    @property
    def hit_rate(self):
        total=self.hits +self.misses

        if total==0:
            return 0.0

        return self.hits/total


cache_metrics=CacheMetrics()